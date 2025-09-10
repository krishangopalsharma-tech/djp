# Path: backend/infrastructure/views.py

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import openpyxl
from .models import Depot, Station, Section, SubSection, Circuit, Supervisor, Equipment, StationEquipment
from .serializers import (
    DepotSerializer,
    StationSerializer,
    SectionSerializer,
    SubSectionSerializer,
    CircuitSerializer,
    SupervisorSerializer,
    EquipmentSerializer,
    StationEquipmentSerializer
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

            depots_created_count = 0
            equipment_created_count = 0
            errors = []
            
            for depot_name, data in depot_data.items():
                try:
                    depot, created = Depot.objects.get_or_create(name=depot_name, defaults={
                        'code': str(data['code']).strip() if data['code'] else '',
                        'location': str(data['location']).strip() if data['location'] else ''
                    })
                    if created:
                        depots_created_count += 1
                    
                    # Clear old equipment before adding new
                    depot.equipments.all().delete()

                    for equip_data in data['equipment']:
                        Equipment.objects.create(depot=depot, **{k: str(v).strip() if v else '' for k, v in equip_data.items()})
                        equipment_created_count += 1
                except Exception as e:
                    errors.append(f"Depot '{depot_name}': {str(e)}")

            return Response({
                "message": "Depot and equipment import complete.",
                "depots_processed": len(depot_data),
                "equipment_created": equipment_created_count,
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
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.data['file']
        try:
            workbook = openpyxl.load_workbook(file_obj)
            sheet = workbook.active
            
            # Use Django's bulk_create for performance
            stations_to_create = []
            equipment_to_create = []
            station_equipment_map = {}
            depot_cache = {d.name: d for d in Depot.objects.all()}

            rows_by_station = {}
            for row_idx in range(2, sheet.max_row + 1):
                station_name = sheet.cell(row=row_idx, column=2).value
                if not station_name: continue
                station_name = station_name.strip()
                
                if station_name not in rows_by_station:
                    rows_by_station[station_name] = {
                        'depot_name': sheet.cell(row=row_idx, column=1).value.strip(),
                        'code': sheet.cell(row=row_idx, column=3).value,
                        'category': sheet.cell(row=row_idx, column=4).value,
                        'equipments': []
                    }
                
                equipment_data = {
                    'name': sheet.cell(row=row_idx, column=5).value,
                    'make_modal': sheet.cell(row=row_idx, column=6).value,
                    'address': sheet.cell(row=row_idx, column=7).value,
                    'location_in_station': sheet.cell(row=row_idx, column=8).value,
                    'quantity': sheet.cell(row=row_idx, column=9).value,
                    'category': sheet.cell(row=row_idx, column=10).value,
                }
                if equipment_data['name']:
                    rows_by_station[station_name]['equipments'].append(equipment_data)
            
            # Delete old stations and their equipment that are in the Excel file
            Station.objects.filter(name__in=rows_by_station.keys()).delete()

            # Create new stations
            for name, data in rows_by_station.items():
                depot = depot_cache.get(data['depot_name'])
                if not depot:
                    depot = Depot.objects.create(name=data['depot_name'])
                    depot_cache[data['depot_name']] = depot
                
                station = Station.objects.create(
                    name=name,
                    depot=depot,
                    code=str(data['code']).strip() if data['code'] else '',
                    category=str(data['category']).strip() if data['category'] else ''
                )
                
                for equip in data['equipments']:
                    equipment_to_create.append(StationEquipment(
                        station=station,
                        name=str(equip['name']).strip() if equip['name'] else '',
                        make_modal=str(equip['make_modal']).strip() if equip['make_modal'] else '',
                        address=str(equip['address']).strip() if equip['address'] else '',
                        location_in_station=str(equip['location_in_station']).strip() if equip['location_in_station'] else '',
                        quantity=equip['quantity'] if equip['quantity'] else 1,
                        category=str(equip['category']).strip() if equip['category'] else ''
                    ))

            StationEquipment.objects.bulk_create(equipment_to_create)

            return Response({
                "message": "Station import successful.",
                "stations_processed": len(rows_by_station),
                "equipment_created": len(equipment_to_create),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related('depot').all().order_by('name')
    serializer_class = SectionSerializer
    permission_classes = [permissions.AllowAny]

class SectionImportView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.data['file']
        try:
            workbook = openpyxl.load_workbook(file_obj)
            sheet = workbook.active
            
            depot_cache = {d.name: d for d in Depot.objects.all()}
            sections_to_create = []

            for row_idx in range(2, sheet.max_row + 1):
                depot_name = sheet.cell(row=row_idx, column=1).value
                section_name = sheet.cell(row=row_idx, column=2).value

                if not depot_name or not section_name:
                    continue

                depot_name = depot_name.strip()
                section_name = section_name.strip()

                depot = depot_cache.get(depot_name)
                if not depot:
                    depot = Depot.objects.create(name=depot_name)
                    depot_cache[depot_name] = depot
                
                sections_to_create.append(Section(name=section_name, depot=depot))

            # Use update_or_create to avoid duplicates
            created_count = 0
            for section in sections_to_create:
                _, created = Section.objects.update_or_create(
                    name=section.name,
                    depot=section.depot,
                    defaults={}
                )
                if created:
                    created_count += 1

            return Response({
                "message": "Sections imported successfully.",
                "created": created_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class SubSectionViewSet(viewsets.ModelViewSet):
    queryset = SubSection.objects.select_related('section').all().order_by('name')
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
                    depot_name = sheet.cell(row=row_idx, column=3).value
                    supervisor_name = sheet.cell(row=row_idx, column=1).value
                    designation = sheet.cell(row=row_idx, column=2).value
                    mobile = sheet.cell(row=row_idx, column=4).value
                    email = sheet.cell(row=row_idx, column=5).value


                    if not supervisor_name:
                        continue

                    depot = None
                    if depot_name:
                        depot, _ = Depot.objects.get_or_create(name=depot_name.strip())

                    supervisor, created = Supervisor.objects.update_or_create(
                        name=supervisor_name.strip(),
                        defaults={
                            'designation': designation.strip() if designation else '',
                            'depot': depot,
                            'mobile': str(mobile).strip() if mobile else '',
                            'email': email.strip() if email else ''
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

