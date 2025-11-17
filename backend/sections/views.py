# Path: backend/sections/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
import pandas as pd
from django.db import transaction
from .models import Section, SubSection, Asset
from depots.models import Depot
from .serializers import (
    SectionSerializer, SubSectionSerializer, AssetSerializer,
    _DepotTreeSerializer
)
from rest_framework.views import APIView
import traceback 
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

class SectionViewSet(viewsets.ModelViewSet):
    """API endpoint for Sections."""
    queryset = Section.objects.select_related('depot').prefetch_related('subsections__assets').all().order_by('depot__name', 'name')
    serializer_class = SectionSerializer
    permission_classes = [permissions.AllowAny] 

    @method_decorator(ensure_csrf_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='import_master_file', parser_classes=[MultiPartParser, FileUploadParser])
    def import_master_file(self, request):
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
            df = df.astype(object).where(pd.notnull(df), None)

            processed_count = 0
            created = {'sections': 0, 'subsections': 0, 'assets': 0}
            updated = {'sections': 0, 'subsections': 0, 'assets': 0}
            skipped = 0
            errors = []
            
            has_depot_name_col = 'Depot Name' in df.columns
            has_depot_code_col = 'Depot' in df.columns

            with transaction.atomic(): 
                for index, row in df.iterrows():
                    section_name = row.get('Section')
                    subsection_name = row.get('sub-Sections') 
                    asset_name = row.get('Asset')
                    
                    if not section_name:
                        errors.append(f"Row {index+2}: Missing Section name.")
                        skipped += 1
                        continue
                    
                    section_name = str(section_name).strip() if section_name else None
                    if not section_name:
                        errors.append(f"Row {index+2}: Section name is blank.")
                        skipped += 1
                        continue

                    depot = None
                    depot_identifier = None
                    try:
                        if has_depot_name_col and row.get('Depot Name'):
                            depot_identifier = str(row.get('Depot Name')).strip()
                            if depot_identifier:
                                depot = Depot.objects.get(name=depot_identifier)
                        
                        elif has_depot_code_col and row.get('Depot'):
                            depot_identifier = str(row.get('Depot')).strip()
                            if depot_identifier:
                                depot = Depot.objects.get(code=depot_identifier)
                        
                        else:
                            errors.append(f"Row {index+2}: Missing 'Depot Name' or 'Depot' (code) column.")
                        
                        if not depot:
                            if depot_identifier: 
                                errors.append(f"Row {index+2}: Depot '{depot_identifier}' not found.")
                            else:
                                errors.append(f"Row {index+2}: Depot column is blank.")
                            skipped += 1
                            continue
                            
                    except Depot.DoesNotExist:
                        errors.append(f"Row {index+2}: Depot '{depot_identifier}' not found.")
                        skipped += 1
                        continue
                    except Depot.MultipleObjectsReturned:
                        errors.append(f"Row {index+2}: Multiple depots found for '{depot_identifier}'.")
                        skipped += 1
                        continue
                    
                    section, section_created = Section.objects.get_or_create(depot=depot, name=section_name)
                    if section_created: created['sections'] += 1
                    
                    subsection = None
                    subsection_name = str(subsection_name).strip() if subsection_name else None
                    if subsection_name:
                        subsection, sub_created = SubSection.objects.get_or_create(section=section, name=subsection_name)
                        if sub_created: created['subsections'] += 1
                    
                    asset_name = str(asset_name).strip() if asset_name else None
                    if asset_name and subsection:
                        quantity_val = row.get('Quantity')
                        unit_val = row.get('Unit')

                        asset_defaults = {}
                        if quantity_val is not None:
                            try:
                                asset_defaults['quantity'] = float(quantity_val)
                            except (ValueError, TypeError):
                                asset_defaults['quantity'] = None
                        
                        unit_val = str(unit_val).strip() if unit_val else None
                        if unit_val:
                            asset_defaults['unit'] = unit_val

                        asset, asset_created = Asset.objects.update_or_create(
                           subsection=subsection,
                           name=asset_name,
                           defaults=asset_defaults
                        )
                        if asset_created:
                            created['assets'] += 1
                        elif any(getattr(asset, k) != v for k, v in asset_defaults.items() if hasattr(asset, k)):
                            updated['assets'] += 1
                        else:
                             skipped +=1
                    elif not section_created:
                         skipped += 1

                    processed_count += 1

            message = (f'Import finished. Processed rows: {processed_count}. '
                       f'Created (Sec/Sub/Ast): {created["sections"]}/{created["subsections"]}/{created["assets"]}. '
                       f'Updated (Sec/Sub/Ast): {updated["sections"]}/{updated["subsections"]}/{updated["assets"]}. '
                       f'Skipped: {skipped}.')

            if errors:
                message += f' Encountered {len(errors)} errors (see details).'
                return Response({'message': message, 'errors': errors[:50]}, status=status.HTTP_207_MULTI_STATUS)

            return Response({'message': message}, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f'An unexpected error occurred during import: {str(e)}.'
            print(f"Import Error: {error_message}") # Log detailed error
            traceback.print_exc() # Print the full traceback to the console
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


class SubSectionViewSet(viewsets.ModelViewSet):
    queryset = SubSection.objects.select_related('section__depot').prefetch_related('assets').all().order_by('section__name', 'name')
    serializer_class = SubSectionSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['section']


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('subsection__section__depot').all().order_by('subsection__name', 'name')
    serializer_class = AssetSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['subsection']

class InfrastructureTreeView(APIView):
    permission_classes = [permissions.AllowAny] # Use AllowAny for dev

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        # --- THIS IS THE FIX ---
        # Prefetch stations and their equipment as well
        queryset = Depot.objects.prefetch_related(
            'sections__subsections__assets',
            'stations__equipments' # <-- ADD THIS LINE
        ).all().order_by('name')
        # --- END OF FIX ---
        
        serializer = _DepotTreeSerializer(queryset, many=True)
        return Response(serializer.data)