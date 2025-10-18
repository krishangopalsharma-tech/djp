# Path: backend/depots/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
from django.http import HttpResponse
import pandas as pd
from .models import Depot, Equipment
from .serializers import DepotSerializer, EquipmentSerializer
import io

class DepotViewSet(viewsets.ModelViewSet):
    """API endpoint for Depots."""
    queryset = Depot.objects.prefetch_related('equipments').all().order_by('name')
    serializer_class = DepotSerializer
    permission_classes = [permissions.AllowAny]
    # ADD THIS LINE to accept file uploads
    parser_classes = [MultiPartParser, FileUploadParser]

    @action(detail=False, methods=['post'])
    def import_from_excel(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # IMPROVEMENT: Handle both CSV and Excel files
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file, engine='openpyxl')

            df.columns = df.columns.str.strip() # Trim whitespace from headers

            depots_processed = 0
            equipment_created = 0
            errors = []

            for index, row in df.iterrows():
                depot_name = row.get('Depot')
                if not depot_name or pd.isna(depot_name):
                    continue
                
                defaults = {}
                if 'Code' in row and pd.notna(row['Code']):
                    defaults['code'] = row['Code']
                if 'Location' in row and pd.notna(row['Location']):
                    defaults['location'] = row['Location']

                depot, created = Depot.objects.update_or_create(
                    name=depot_name,
                    defaults=defaults
                )
                depots_processed += 1

                if 'Equipment Name' in row and pd.notna(row['Equipment Name']):
                    Equipment.objects.update_or_create(
                        depot=depot,
                        name=row.get('Equipment Name'),
                        defaults={
                            'model_type': row.get('Model/Type', ''),
                            'asset_id': row.get('Asset ID', ''),
                            'location_in_depot': row.get('Location in Depot', ''),
                            'notes': row.get('Notes', '')
                        }
                    )
                    equipment_created += 1
            
            return Response({
                'message': f'Import successful. Depots processed: {depots_processed}, Equipment created/updated: {equipment_created}.',
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'An error occurred during import: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_to_excel(self, request):
        depots = Depot.objects.prefetch_related('equipments').all()
        data = []
        for depot in depots:
            if depot.equipments.exists():
                for equipment in depot.equipments.all():
                    data.append({
                        'Depot': depot.name, 'Code': depot.code, 'Location': depot.location,
                        'Equipment Name': equipment.name, 'Model/Type': equipment.model_type,
                        'Asset ID': equipment.asset_id, 'Location in Depot': equipment.location_in_depot,
                        'Notes': equipment.notes,
                    })
            else:
                data.append({
                    'Depot': depot.name, 'Code': depot.code, 'Location': depot.location,
                    'Equipment Name': None, 'Model/Type': None, 'Asset ID': None, 'Location in Depot': None, 'Notes': None,
                })
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Depots and Equipment')
        output.seek(0)
        response = HttpResponse(
            output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="depot_equipment_export.xlsx"'
        return response

class EquipmentViewSet(viewsets.ModelViewSet):
    """API endpoint for Equipment."""
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.AllowAny]