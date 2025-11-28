# Path: backend/depots/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
from django.http import HttpResponse
import pandas as pd
from django.db import transaction ## ADD THIS IMPORT
from .models import Depot, Equipment
from .serializers import DepotSerializer, EquipmentSerializer
import io

class DepotViewSet(viewsets.ModelViewSet):
    """API endpoint for Depots."""
    queryset = Depot.objects.prefetch_related('equipments').all().order_by('name')
    serializer_class = DepotSerializer
    permission_classes = [permissions.AllowAny]
    # --- CRITICAL: Ensure NO parser_classes line is here ---

    @action(detail=False, methods=['post'], url_path='import_from_excel', parser_classes=[MultiPartParser, FileUploadParser])
    def import_from_excel(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if file.name.endswith('.csv'):
                try: df = pd.read_csv(file, encoding='utf-8')
                except UnicodeDecodeError: df = pd.read_csv(file, encoding='latin1')
            else:
                df = pd.read_excel(file, engine='openpyxl')

            df.columns = df.columns.str.strip()
            # Convert potential float NaNs or None strings to actual None for consistency
            df = df.astype(object).where(pd.notnull(df), None) # Use object dtype to prevent int conversion issues

            depots_created = 0
            depots_updated = 0
            equipment_created = 0
            equipment_updated = 0
            rows_skipped = 0
            errors = []

            with transaction.atomic(): # Use transaction for atomicity
                for index, row in df.iterrows():
                    depot_name = row.get('Depot')
                    if not depot_name: # Skip rows without a depot name
                        errors.append(f"Row {index+2}: Missing Depot name.")
                        continue
                    depot_name = str(depot_name).strip()

                    # Prepare data from row, handling None/NaN
                    code_from_file = row.get('depot code')
                    code_from_file = str(code_from_file).strip() if code_from_file is not None else None
                    location_from_file = row.get('location')
                    location_from_file = str(location_from_file).strip() if location_from_file is not None else None

                    # --- Refined Update/Create Logic ---
                    try:
                        depot = Depot.objects.get(name=depot_name)
                        # Depot exists, check if update is needed
                        needs_update = False
                        update_fields = {}
                        if depot.code != code_from_file and code_from_file is not None:
                            update_fields['code'] = code_from_file
                            needs_update = True
                        if depot.location != location_from_file and location_from_file is not None:
                            update_fields['location'] = location_from_file
                            needs_update = True

                        if needs_update:
                            for field, value in update_fields.items():
                                setattr(depot, field, value)
                            depot.save(update_fields=update_fields.keys())
                            depots_updated += 1
                        # else: # No changes needed for depot itself
                        #    rows_skipped +=1 # Only increment if BOTH depot and equip skip

                    except Depot.DoesNotExist:
                        # Depot does not exist, create it
                        depot = Depot.objects.create(
                            name=depot_name,
                            code=code_from_file,
                            location=location_from_file
                        )
                        depots_created += 1

                    # --- Process Equipment ---
                    equipment_name = row.get('Measuring Equipment')
                    if equipment_name and pd.notna(equipment_name):
                        equipment_name = str(equipment_name).strip()
                        
                        # Prepare equipment data from row
                        defaults_eq = {}
                        if 'Model / Type' in row and pd.notna(row['Model / Type']): defaults_eq['model_type'] = str(row['Model / Type']).strip()
                        if 'Asset / Serial ID' in row and pd.notna(row['Asset / Serial ID']): defaults_eq['asset_id'] = str(row['Asset / Serial ID']).strip()
                        if 'Location in Depot' in row and pd.notna(row['Location in Depot']): defaults_eq['location_in_depot'] = str(row['Location in Depot']).strip()
                        elif location_from_file: defaults_eq['location_in_depot'] = location_from_file # Fallback to depot location
                        if 'Notes' in row and pd.notna(row['Notes']): defaults_eq['notes'] = str(row['Notes']).strip()
                        if 'Quantity' in row and pd.notna(row['Quantity']):
                            try: defaults_eq['quantity'] = int(float(row['Quantity'])) # Try converting to int
                            except (ValueError, TypeError): pass # Ignore invalid quantity for now

                        # Check if equipment exists and needs update
                        try:
                            equipment = Equipment.objects.get(depot=depot, name=equipment_name)
                            needs_eq_update = False
                            for field, value in defaults_eq.items():
                                if getattr(equipment, field) != value:
                                    setattr(equipment, field, value)
                                    needs_eq_update = True
                            
                            if needs_eq_update:
                                equipment.save(update_fields=defaults_eq.keys())
                                equipment_updated += 1
                            elif not needs_update: # If depot also didn't need update, skip row count
                                rows_skipped +=1
                                
                        except Equipment.DoesNotExist:
                             Equipment.objects.create(depot=depot, name=equipment_name, **defaults_eq)
                             equipment_created += 1
                    elif not needs_update: # No equipment in row AND depot didn't need update
                         rows_skipped +=1


            message = (f'Import finished. Depots created: {depots_created}, updated: {depots_updated}. '
                       f'Equipment created: {equipment_created}, updated: {equipment_updated}. Rows skipped: {rows_skipped}.')
            if errors:
                message += f' Encountered {len(errors)} errors (see details).'
                return Response({'message': message, 'errors': errors[:50]}, status=status.HTTP_207_MULTI_STATUS)

            return Response({'message': message}, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f'An unexpected error occurred during import: {str(e)}.'
            print(f"Import Error: {error_message}") # Log detailed error
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'], url_path='export_to_excel')
    def export_to_excel(self, request):
        # ... (export logic remains the same) ...
        depots = Depot.objects.prefetch_related('equipments').all()
        data = []
        # Match export headers to expected import headers
        export_columns = [ 'Depot', 'depot code', 'location', 'Measuring Equipment', 'Model / Type', 'Asset / Serial ID', 'Quantity', 'Location in Depot', 'Notes']
        for depot in depots:
            if depot.equipments.exists():
                for equipment in depot.equipments.all():
                    data.append({
                        'Depot': depot.name, 'depot code': depot.code, 'location': depot.location,
                        'Measuring Equipment': equipment.name, 'Model / Type': equipment.model_type,
                        'Asset / Serial ID': equipment.asset_id, 'Quantity': equipment.quantity, # Add quantity if needed in export
                        'Location in Depot': equipment.location_in_depot, 'Notes': equipment.notes,
                    })
            else:
                 data.append({ 'Depot': depot.name, 'depot code': depot.code, 'location': depot.location, 'Measuring Equipment': None, 'Model / Type': None, 'Asset / Serial ID': None, 'Quantity': None, 'Location in Depot': None, 'Notes': None })

        df = pd.DataFrame(data, columns=export_columns) # Ensure columns are ordered
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Depots and Equipment')
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="depot_equipment_export.xlsx"'
        return response


class EquipmentViewSet(viewsets.ModelViewSet):
    """API endpoint for Equipment."""
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.AllowAny]