# Path: backend/stations/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
import pandas as pd
from django.db import transaction
from django.http import HttpResponse
import io
from .models import Station, StationEquipment
from depots.models import Depot
from .serializers import StationSerializer, StationEquipmentSerializer
import traceback # Import for detailed error logging

class StationViewSet(viewsets.ModelViewSet):
    """API endpoint for Stations."""
    queryset = Station.objects.select_related('depot').prefetch_related('equipments').all().order_by('depot__name', 'name')
    serializer_class = StationSerializer
    permission_classes = [permissions.AllowAny] # Dev setting

    @action(detail=False, methods=['post'], url_path='import_stations_file', parser_classes=[MultiPartParser, FileUploadParser])
    def import_stations_file(self, request):
        file = request.FILES.get('file')
        if not file: return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # ... (read csv/excel logic) ...
            if file.name.endswith('.csv'):
                try: df = pd.read_csv(file, encoding='utf-8')
                except UnicodeDecodeError: df = pd.read_csv(file, encoding='latin1')
            else: df = pd.read_excel(file, engine='openpyxl')
            
            df.columns = df.columns.str.strip()
            df = df.astype(object).where(pd.notnull(df), None)
            
            processed_count = 0; created = {'stations': 0, 'equipments': 0}; updated = {'stations': 0, 'equipments': 0}; skipped = 0; errors = []
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    depot_code_from_file = row.get('Depot')
                    station_name = row.get('Sation Name') # Still use 'Sation Name' (with typo)
                    # --- FIX: Use 'Station Code' as the main key ---
                    station_code_from_file = row.get('Station Code')

                    if not depot_code_from_file or not station_name or not station_code_from_file: 
                        errors.append(f"Row {index+2}: Missing Depot, Station Name, or Station Code."); skipped += 1; continue
                    
                    depot_code_from_file = str(depot_code_from_file).strip()
                    station_name = str(station_name).strip()
                    station_code_from_file = str(station_code_from_file).strip()
                    
                    try: depot = Depot.objects.get(code=depot_code_from_file)
                    except Depot.DoesNotExist: errors.append(f"Row {index+2}: Depot with code '{depot_code_from_file}' not found."); skipped += 1; continue
                    except Depot.MultipleObjectsReturned: errors.append(f"Row {index+2}: Multiple depots found for code '{depot_code_from_file}'."); skipped += 1; continue
                    
                    # --- FIX: Use 'code' for lookup, update 'name' and 'category' in defaults ---
                    station_defaults = {
                        'depot': depot,
                        'name': station_name
                    }
                    if 'Category' in row and pd.notna(row['Category']): 
                        station_defaults['category'] = str(row['Category']).strip()
                    
                    # Use Station Code as the unique lookup key
                    station, station_created = Station.objects.update_or_create(
                        code=station_code_from_file, 
                        defaults=station_defaults
                    )
                    
                    if station_created: created['stations'] += 1
                    elif any(getattr(station, k, None) != v for k, v in station_defaults.items()): updated['stations'] += 1
                    
                    # --- Equipment logic (remains mostly the same) ---
                    equip_name = row.get('Equipment Name')
                    if equip_name and pd.notna(equip_name):
                        equip_name = str(equip_name).strip()
                        if equip_name:
                            equip_defaults = {}
                            make = str(row.get('Make', '') or '').strip()
                            model = str(row.get('Model', '') or '').strip()
                            if make and model: equip_defaults['make_modal'] = f"{make} / {model}"
                            elif make: equip_defaults['make_modal'] = make
                            elif model: equip_defaults['make_modal'] = model
                            if 'Address' in row and pd.notna(row['Address']): equip_defaults['address'] = str(row['Address']).strip()
                            if 'Location' in row and pd.notna(row['Location']): equip_defaults['location_in_station'] = str(row['Location']).strip()
                            if 'Equipment Category' in row and pd.notna(row['Equipment Category']): equip_defaults['category'] = str(row['Equipment Category']).strip()
                            elif 'Category' in row and pd.notna(row['Category']): equip_defaults['category'] = str(row['Category']).strip()
                            if 'Quantity' in row and pd.notna(row['Quantity']):
                                try: equip_defaults['quantity'] = int(float(row['Quantity']))
                                except (ValueError, TypeError): pass 
                            
                            equipment, equip_created = StationEquipment.objects.update_or_create(station=station, name=equip_name, defaults=equip_defaults)
                            
                            if equip_created: created['equipments'] += 1
                            elif any(getattr(equipment, k, None) != v for k, v in equip_defaults.items()): updated['equipments'] += 1
                            else: skipped += (not station_created and not any(getattr(station, k, None) != v for k, v in station_defaults.items()))
                        else: skipped += (not station_created and not any(getattr(station, k, None) != v for k, v in station_defaults.items()))
                    elif not station_created and not any(getattr(station, k, None) != v for k, v in station_defaults.items()):
                        skipped += 1
                    
                    processed_count += 1
            
            # ... (rest of message and response logic remains the same) ...
            message = (f'Import done. Rows processed: {processed_count}. Created(Stn/Eqp): {created["stations"]}/{created["equipments"]}. Updated(Stn/Eqp): {updated["stations"]}/{updated["equipments"]}. Skipped: {skipped}.')
            status_code = status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK
            return Response({'message': message, 'errors': errors[:50]}, status=status_code)
        
        except Exception as e:
            error_message = f'Import error: {str(e)}.'
            print(f"Import Error: {error_message}")
            traceback.print_exc()
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='export_to_excel')
    def export_to_excel(self, request):
        stations = Station.objects.select_related('depot').prefetch_related('equipments').all().order_by('depot__name', 'name')
        data = []
        # --- FIX: Match export headers to your import headers ---
        export_columns = ['Depot', 'Sation Name', 'Station Code', 'Category', 'Equipment Name', 'Make', 'Model', 'Address', 'Location', 'Quantity']
        for station in stations:
            if station.equipments.exists():
                for equip in station.equipments.all():
                    # Split make_modal back into Make and Model
                    make, model = (equip.make_modal.split(' / ') + [''])[:2] if equip.make_modal and ' / ' in equip.make_modal else (equip.make_modal, '')
                    data.append({
                        'Depot': station.depot.code or station.depot.name, 
                        'Sation Name': station.name, 
                        'Station Code': station.code, 
                        'Category': station.category, 
                        'Equipment Name': equip.name, 
                        'Make': make, 
                        'Model': model, 
                        'Address': equip.address, 
                        'Location': equip.location_in_station, 
                        'Quantity': equip.quantity
                    })
            else: 
                data.append({
                    'Depot': station.depot.code or station.depot.name, 
                    'Sation Name': station.name, 
                    'Station Code': station.code, 
                    'Category': station.category, 
                    'Equipment Name': None, 'Make': None, 'Model': None, 'Address': None, 'Location': None, 'Quantity': None
                })
        if not data: data.append({col: None for col in export_columns})
        df = pd.DataFrame(data, columns=export_columns); output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False, sheet_name='Stations & Equipment')
        output.seek(0); response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'); response['Content-Disposition'] = 'attachment; filename="stations_equipment_export.xlsx"'; return response

class StationEquipmentViewSet(viewsets.ModelViewSet):
    """API endpoint for Station Equipment."""
    queryset = StationEquipment.objects.select_related('station__depot').all().order_by('station__name', 'name')
    serializer_class = StationEquipmentSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['station']