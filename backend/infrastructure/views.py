# Path: backend/infrastructure/views.py

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import openpyxl
from django.db import transaction

from .models import (
    Depot, Station, Section, SubSection, Circuit, Supervisor, 
    Equipment, StationEquipment, Asset
)
from .serializers import (
    DepotSerializer, StationSerializer, SectionSerializer, SubSectionSerializer,
    CircuitSerializer, SupervisorSerializer, EquipmentSerializer, StationEquipmentSerializer
)

class DepotViewSet(viewsets.ModelViewSet):
    queryset = Depot.objects.prefetch_related('equipments').all().order_by('name')
    serializer_class = DepotSerializer
    permission_classes = [permissions.AllowAny]

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.select_related('depot').all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.AllowAny]

class StationEquipmentViewSet(viewsets.ModelViewSet):
    queryset = StationEquipment.objects.select_related('station').all()
    serializer_class = StationEquipmentSerializer
    permission_classes = [permissions.AllowAny]

class DepotImportView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.data['file']
        try:
            workbook = openpyxl.load_workbook(file_obj)
            sheet = workbook.active
            depots_created = 0
            equipment_created = 0
            errors = []
            
            depot_data = {}
            for row_idx in range(2, sheet.max_row + 1):
                depot_name = sheet.cell(row=row_idx, column=1).value
                if depot_name:
                    depot_name = depot_name.strip()
                    if depot_name not in depot_data:
                        depot_data[depot_name] = {
                            'code': sheet.cell(row=row_idx, column=2).value,
                            'location': sheet.cell(row=row_idx, column=3).value,
                            'equipment': []
                        }
                    
                    equipment = {
                        'name': sheet.cell(row=row_idx, column=4).value,
                        'model_type': sheet.cell(row=row_idx, column=5).value,
                        'asset_id': sheet.cell(row=row_idx, column=6).value,
                        'location_in_depot': sheet.cell(row=row_idx, column=7).value,
                        'notes': sheet.cell(row=row_idx, column=8).value
                    }
                    if equipment['name']:
                        depot_data[depot_name]['equipment'].append(equipment)

            with transaction.atomic():
                for depot_name, data in depot_data.items():
                    try:
                        depot, created = Depot.objects.get_or_create(
                            name=depot_name,
                            defaults={
                                'code': str(data['code']).strip() if data['code'] else '',
                                'location': str(data['location']).strip() if data['location'] else ''
                            }
                        )
                        if created:
                            depots_created += 1
                        
                        Equipment.objects.filter(depot=depot).delete()
                        
                        equip_to_create = []
                        for equip_data in data['equipment']:
                            equip_to_create.append(Equipment(
                                depot=depot,
                                name=str(equip_data['name']).strip(),
                                model_type=str(equip_data['model_type']).strip() if equip_data['model_type'] else '',
                                asset_id=str(equip_data['asset_id']).strip() if equip_data['asset_id'] else '',
                                location_in_depot=str(equip_data['location_in_depot']).strip() if equip_data['location_in_depot'] else '',
                                notes=str(equip_data['notes']).strip() if equip_data['notes'] else ''
                            ))
                        Equipment.objects.bulk_create(equip_to_create)
                        equipment_created += len(equip_to_create)

                    except Exception as e:
                        errors.append(f"Depot '{depot_name}': {str(e)}")

            return Response({
                "message": "Depot and equipment import complete.",
                "depots_processed": len(depot_data),
                "equipment_created": equipment_created,
                "errors": errors
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.select_related('depot').prefetch_related('equipments').all().order_by('name')
    serializer_class = StationSerializer
    permission_classes = [permissions.AllowAny]

class StationImportView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.data['file']
        try:
            workbook = openpyxl.load_workbook(file_obj)
            sheet = workbook.active
            
            station_data = {}
            
            for row_idx in range(2, sheet.max_row + 1):
                depot_name = sheet.cell(row=row_idx, column=1).value
                station_name = sheet.cell(row=row_idx, column=2).value
                
                if not depot_name or not station_name:
                    continue

                depot_name = depot_name.strip()
                station_name = station_name.strip()
                station_key = f"{depot_name}::{station_name}"

                if station_key not in station_data:
                    station_data[station_key] = {
                        'depot_name': depot_name,
                        'station_name': station_name,
                        'code': sheet.cell(row=row_idx, column=3).value,
                        'category': sheet.cell(row=row_idx, column=4).value,
                        'equipments': []
                    }

                equipment = {
                    'name': sheet.cell(row=row_idx, column=5).value,
                    'make_modal': sheet.cell(row=row_idx, column=6).value,
                    'address': sheet.cell(row=row_idx, column=7).value,
                    'location_in_station': sheet.cell(row=row_idx, column=8).value,
                    'quantity': sheet.cell(row=row_idx, column=9).value,
                    'category': station_data[station_key]['category'] # Inherit category for equipment
                }
                if equipment['name']:
                    station_data[station_key]['equipments'].append(equipment)
            
            created_stations = 0
            created_equipment = 0
            errors = []

            with transaction.atomic():
                all_depots = {d.name: d for d in Depot.objects.all()}
                
                for key, data in station_data.items():
                    try:
                        depot = all_depots.get(data['depot_name'])
                        if not depot:
                            errors.append(f"Depot '{data['depot_name']}' not found for station '{data['station_name']}'. Please create it first.")
                            continue

                        station, created = Station.objects.get_or_create(
                            name=data['station_name'],
                            depot=depot,
                            defaults={
                                'code': str(data['code']).strip() if data['code'] else '',
                                'category': str(data['category']).strip() if data['category'] else ''
                            }
                        )
                        if created:
                            created_stations += 1
                        
                        StationEquipment.objects.filter(station=station).delete()

                        equip_to_create = []
                        for equip_data in data['equipments']:
                             equip_to_create.append(StationEquipment(
                                station=station,
                                name=str(equip_data['name']).strip(),
                                category=str(equip_data['category']).strip() if equip_data['category'] else '',
                                make_modal=str(equip_data['make_modal']).strip() if equip_data['make_modal'] else '',
                                address=str(equip_data['address']).strip() if equip_data['address'] else '',
                                location_in_station=str(equip_data['location_in_station']).strip() if equip_data['location_in_station'] else '',
                                quantity=int(equip_data['quantity']) if equip_data['quantity'] else 1
                            ))
                        StationEquipment.objects.bulk_create(equip_to_create)
                        created_equipment += len(equip_to_create)

                    except Exception as e:
                        errors.append(f"Station '{data['station_name']}': {str(e)}")

            if errors:
                 return Response({
                    "message": "Import finished with errors.",
                    "stations_created": created_stations,
                    "equipment_created": created_equipment,
                    "errors": errors
                }, status=status.HTTP_400_BAD_REQUEST)


            return Response({
                "message": "Station and equipment import complete.",
                "stations_created": created_stations,
                "equipment_created": created_equipment
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related('depot').prefetch_related('subsections__assets').all().order_by('name')
    serializer_class = SectionSerializer
    permission_classes = [permissions.AllowAny]

class SectionImportView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.data['file']
        try:
            workbook = openpyxl.load_workbook(file_obj)
            sheet = workbook.active
            
            # --- 1. Pre-validation and Data Grouping ---
            required_depots = set()
            hierarchy = {}
            for row_idx in range(2, sheet.max_row + 1):
                depot_name = sheet.cell(row=row_idx, column=1).value
                section_name = sheet.cell(row=row_idx, column=2).value
                subsection_name = sheet.cell(row=row_idx, column=3).value
                asset_name = sheet.cell(row=row_idx, column=4).value

                if not depot_name or not section_name or not subsection_name or not asset_name:
                    continue 

                depot_name = depot_name.strip()
                section_name = section_name.strip()
                subsection_name = subsection_name.strip()

                required_depots.add(depot_name)

                if depot_name not in hierarchy:
                    hierarchy[depot_name] = {}
                if section_name not in hierarchy[depot_name]:
                    hierarchy[depot_name][section_name] = {}
                if subsection_name not in hierarchy[depot_name][section_name]:
                    hierarchy[depot_name][section_name][subsection_name] = []

                asset_data = {
                    'name': asset_name,
                    'quantity': sheet.cell(row=row_idx, column=5).value,
                    'unit': sheet.cell(row=row_idx, column=6).value
                }
                hierarchy[depot_name][section_name][subsection_name].append(asset_data)
            
            # --- 2. Depot Validation ---
            existing_depots = set(Depot.objects.filter(name__in=required_depots).values_list('name', flat=True))
            missing_depots = required_depots - existing_depots
            if missing_depots:
                return Response(
                    {"error": f"Upload failed. The following depots do not exist and must be created first: {', '.join(sorted(list(missing_depots)))}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # --- 3. Process the Hierarchy ---
            depot_map = {d.name: d for d in Depot.objects.filter(name__in=required_depots)}
            created_sections = 0
            created_subsections = 0
            created_assets = 0

            # Clear old assets for the subsections being imported
            subsections_to_clear = SubSection.objects.filter(
                section__depot__name__in=hierarchy.keys(),
                section__name__in=[s for d in hierarchy.values() for s in d.keys()],
                name__in=[ss for d in hierarchy.values() for s in d.values() for ss in s.keys()]
            )
            Asset.objects.filter(subsection__in=subsections_to_clear).delete()

            for depot_name, sections in hierarchy.items():
                depot_obj = depot_map[depot_name]
                for section_name, subsections in sections.items():
                    section_obj, s_created = Section.objects.get_or_create(depot=depot_obj, name=section_name)
                    if s_created:
                        created_sections += 1
                    
                    for subsection_name, assets in subsections.items():
                        subsection_obj, ss_created = SubSection.objects.get_or_create(section=section_obj, name=subsection_name)
                        if ss_created:
                            created_subsections += 1
                        
                        assets_to_create = []
                        for asset in assets:
                            assets_to_create.append(Asset(
                                subsection=subsection_obj,
                                name=str(asset['name']).strip(),
                                quantity=asset['quantity'],
                                unit=str(asset['unit']).strip() if asset['unit'] else ''
                            ))
                        
                        Asset.objects.bulk_create(assets_to_create)
                        created_assets += len(assets_to_create)

            return Response({
                "message": "Master infrastructure import complete.",
                "sections_processed": created_sections,
                "subsections_processed": created_subsections,
                "assets_created": created_assets
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubSectionViewSet(viewsets.ModelViewSet):
    queryset = SubSection.objects.select_related('section').prefetch_related('assets').all().order_by('name')
    serializer_class = SubSectionSerializer
    permission_classes = [permissions.AllowAny]

class CircuitViewSet(viewsets.ModelViewSet):
    queryset = Circuit.objects.all().order_by('circuit_id')
    serializer_class = CircuitSerializer
    permission_classes = [permissions.AllowAny]

class SupervisorViewSet(viewsets.ModelViewSet):
    queryset = Supervisor.objects.select_related('depot').all().order_by('name')
    serializer_class = SupervisorSerializer
    permission_classes = [permissions.AllowAny]

class SupervisorImportView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.data['file']
        try:
            workbook = openpyxl.load_workbook(file_obj)
            sheet = workbook.active
            created_count = 0
            updated_count = 0
            errors = []

            for row_idx in range(2, sheet.max_row + 1):
                try:
                    name = sheet.cell(row=row_idx, column=1).value
                    designation = sheet.cell(row=row_idx, column=2).value
                    depot_name = sheet.cell(row=row_idx, column=3).value
                    mobile = sheet.cell(row=row_idx, column=4).value
                    email = sheet.cell(row=row_idx, column=5).value

                    if not name:
                        continue

                    depot = None
                    if depot_name:
                        depot, _ = Depot.objects.get_or_create(name=depot_name.strip())

                    supervisor, created = Supervisor.objects.update_or_create(
                        name=name.strip(),
                        defaults={
                            'designation': str(designation).strip() if designation else '',
                            'depot': depot,
                            'mobile': str(mobile).strip() if mobile else '',
                            'email': str(email).strip() if email else ''
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    errors.append(f"Row {row_idx}: {str(e)}")

            return Response({
                "message": "Supervisor import complete.",
                "created": created_count,
                "updated": updated_count,
                "errors": errors
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

