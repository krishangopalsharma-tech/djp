# Path: backend/circuits/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
import pandas as pd
from django.db import transaction
from django.http import HttpResponse
import io
from .models import Circuit
from .serializers import CircuitSerializer
import traceback

class CircuitViewSet(viewsets.ModelViewSet):
    """API endpoint for Circuits."""
    queryset = Circuit.objects.all().order_by('circuit_id')
    serializer_class = CircuitSerializer
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
            valid_severities = ['Minor', 'Major', 'Critical']

            with transaction.atomic():
                for index, row in df.iterrows():
                    circuit_id = row.get('Circuit ID')
                    if not circuit_id or pd.isna(circuit_id):
                        errors.append(f"Row {index+2}: Missing 'Circuit ID'.")
                        skipped_count += 1
                        continue
                    
                    circuit_id = str(circuit_id).strip()
                    
                    defaults = {}
                    if 'Name' in row and pd.notna(row['Name']): defaults['name'] = str(row['Name']).strip()
                    if 'Related Equipment' in row and pd.notna(row['Related Equipment']): defaults['related_equipment'] = str(row['Related Equipment']).strip()
                    if 'Details' in row and pd.notna(row['Details']): defaults['details'] = str(row['Details']).strip()
                    if 'Severity' in row and pd.notna(row['Severity']):
                        severity = str(row['Severity']).strip().title()
                        if severity in valid_severities:
                            defaults['severity'] = severity
                        else:
                            errors.append(f"Row {index+2}: Invalid severity '{row['Severity']}'. Defaulting to 'Minor'.")
                            defaults['severity'] = 'Minor'
                    
                    circuit, created = Circuit.objects.update_or_create(
                        circuit_id=circuit_id,
                        defaults=defaults
                    )
                    
                    if created: created_count += 1
                    elif any(getattr(circuit, k, None) != v for k, v in defaults.items()): updated_count += 1
                    else: skipped_count += 1
            
            message = (f'Import complete. Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}.')
            status_code = status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK
            return Response({'message': message, 'errors': errors[:50]}, status=status_code)

        except Exception as e:
            error_message = f'Import error: {str(e)}.'
            traceback.print_exc()
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='export_to_excel')
    def export_to_excel(self, request):
        circuits = Circuit.objects.all()
        data = []
        export_columns = ['Circuit ID', 'Name', 'Related Equipment', 'Severity', 'Details']
        
        for c in circuits:
            data.append({
                'Circuit ID': c.circuit_id,
                'Name': c.name,
                'Related Equipment': c.related_equipment,
                'Severity': c.severity,
                'Details': c.details
            })

        if not data: data.append({col: None for col in export_columns})
        df = pd.DataFrame(data, columns=export_columns); output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False, sheet_name='Circuits')
        output.seek(0); response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="circuits_export.xlsx"'; return response