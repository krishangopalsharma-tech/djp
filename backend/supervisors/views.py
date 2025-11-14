# Path: backend/supervisors/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
import pandas as pd
from django.db import transaction
from django.http import HttpResponse
import io
from .models import Supervisor
from depots.models import Depot
from .serializers import SupervisorSerializer
import traceback # Import for detailed error logging

class SupervisorViewSet(viewsets.ModelViewSet):
    """API endpoint for Supervisors."""
    queryset = Supervisor.objects.select_related('depot', 'user').all().order_by('name')
    serializer_class = SupervisorSerializer
    permission_classes = [permissions.AllowAny] # Dev setting

    @action(detail=False, methods=['post'], url_path='import_from_excel', parser_classes=[MultiPartParser, FileUploadParser])
    def import_from_excel(self, request):
        file = request.FILES.get('file')
        if not file: return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if file.name.endswith('.csv'):
                try: df = pd.read_csv(file, encoding='utf-8')
                except UnicodeDecodeError: df = pd.read_csv(file, encoding='latin1')
            else: df = pd.read_excel(file, engine='openpyxl')
            
            df.columns = df.columns.str.strip()
            df = df.astype(object).where(pd.notnull(df), None)

            created_count = 0; updated_count = 0; skipped_count = 0; errors = []

            with transaction.atomic():
                for index, row in df.iterrows():
                    supervisor_name = row.get('Supervisor')
                    if not supervisor_name or pd.isna(supervisor_name):
                        errors.append(f"Row {index+2}: Missing Supervisor name.")
                        skipped_count += 1
                        continue
                    
                    supervisor_name = str(supervisor_name).strip()
                    depot_code = row.get('Depot Code') # Expecting Depot Code
                    
                    depot = None
                    if depot_code and pd.notna(depot_code):
                        depot_code = str(depot_code).strip()
                        try:
                            depot = Depot.objects.get(code=depot_code)
                        except Depot.DoesNotExist:
                            errors.append(f"Row {index+2}: Depot with code '{depot_code}' not found. Supervisor will be created without depot.")
                        except Depot.MultipleObjectsReturned:
                            errors.append(f"Row {index+2}: Multiple depots found for code '{depot_code}'. Supervisor will be created without depot.")
                    
                    defaults = {'depot': depot}
                    if 'Designation' in row and pd.notna(row['Designation']): defaults['designation'] = str(row['Designation']).strip()
                    if 'Mobile' in row and pd.notna(row['Mobile']): defaults['mobile'] = str(row['Mobile']).strip()
                    if 'Email' in row and pd.notna(row['Email']): defaults['email'] = str(row['Email']).strip()
                    
                    supervisor, created = Supervisor.objects.update_or_create(
                        name=supervisor_name,
                        defaults=defaults
                    )
                    
                    if created: created_count += 1
                    elif any(getattr(supervisor, k, None) != v for k, v in defaults.items()): updated_count += 1
                    else: skipped_count += 1
            
            message = (f'Import complete. Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}.')
            status_code = status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK
            return Response({'message': message, 'errors': errors[:50]}, status=status_code)

        except Exception as e:
            error_message = f'Import error: {str(e)}.'
            traceback.print_exc() # Log full traceback
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='export_to_excel')
    def export_to_excel(self, request):
        supervisors = Supervisor.objects.select_related('depot').all()
        data = []
        export_columns = ['Supervisor', 'Designation', 'Depot Code', 'Mobile', 'Email']
        
        for s in supervisors:
            data.append({
                'Supervisor': s.name,
                'Designation': s.designation,
                'Depot Code': s.depot.code if s.depot else None,
                'Mobile': s.mobile,
                'Email': s.email
            })

        if not data: data.append({col: None for col in export_columns})
        df = pd.DataFrame(data, columns=export_columns); output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False, sheet_name='Supervisors')
        output.seek(0); response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="supervisors_export.xlsx"'; return response