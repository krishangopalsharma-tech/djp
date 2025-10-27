# Path: backend/sections/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
import pandas as pd
from django.db import transaction
from .models import Section, SubSection, Asset
from depots.models import Depot
from .serializers import SectionSerializer, SubSectionSerializer, AssetSerializer

class SectionViewSet(viewsets.ModelViewSet):
    """API endpoint for Sections."""
    # Optimized queryset using select_related and prefetch_related
    queryset = Section.objects.select_related('depot').prefetch_related('subsections__assets').all().order_by('depot__name', 'name')
    serializer_class = SectionSerializer
    permission_classes = [permissions.AllowAny] # Use AllowAny for development

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
            # Convert NaN/None strings to actual None, treat all columns as objects first
            df = df.astype(object).where(pd.notnull(df), None)

            processed_count = 0
            created = {'sections': 0, 'subsections': 0, 'assets': 0}
            updated = {'sections': 0, 'subsections': 0, 'assets': 0}
            skipped = 0
            errors = []

            with transaction.atomic(): # Use a transaction for atomic import
                for index, row in df.iterrows():
                    depot_name = row.get('Depot')
                    section_name = row.get('Section')
                    subsection_name = row.get('Sub-section') # Match common header
                    asset_name = row.get('Asset')

                    if not depot_name or not section_name:
                        errors.append(f"Row {index+2}: Missing Depot or Section name.")
                        skipped += 1
                        continue
                    depot_name = str(depot_name).strip()
                    section_name = str(section_name).strip()

                    try:
                        depot = Depot.objects.get(name=depot_name)
                    except Depot.DoesNotExist:
                        errors.append(f"Row {index+2}: Depot '{depot_name}' not found.")
                        skipped += 1
                        continue

                    # --- Section Update/Create ---
                    section, section_created = Section.objects.get_or_create(depot=depot, name=section_name)
                    if section_created: created['sections'] += 1
                    # No updatable fields on Section currently besides name/depot link

                    # --- SubSection Update/Create ---
                    subsection = None
                    if subsection_name and pd.notna(subsection_name):
                        subsection_name = str(subsection_name).strip()
                        subsection, sub_created = SubSection.objects.get_or_create(section=section, name=subsection_name)
                        if sub_created: created['subsections'] += 1
                        # No updatable fields on SubSection currently

                    # --- Asset Update/Create ---
                    if asset_name and pd.notna(asset_name) and subsection:
                        asset_name = str(asset_name).strip()
                        quantity_val = row.get('Quantity')
                        unit_val = row.get('Unit')

                        asset_defaults = {}
                        valid_quantity = True
                        if quantity_val is not None:
                            try:
                                asset_defaults['quantity'] = float(quantity_val) # Store as float/decimal
                            except (ValueError, TypeError):
                                errors.append(f"Row {index+2}: Invalid quantity '{quantity_val}' for asset '{asset_name}'. Using null.")
                                asset_defaults['quantity'] = None
                                valid_quantity = False
                        if unit_val is not None:
                            asset_defaults['unit'] = str(unit_val).strip()

                        asset, asset_created = Asset.objects.update_or_create(
                           subsection=subsection,
                           name=asset_name,
                           defaults=asset_defaults
                        )
                        if asset_created:
                             created['assets'] += 1
                        # Check if update occurred (update_or_create doesn't directly tell us)
                        elif any(getattr(asset, k) != v for k, v in asset_defaults.items() if hasattr(asset, k)):
                             updated['assets'] += 1
                        else:
                             skipped +=1 # Increment skipped only if nothing changed

                    elif not section_created: # No asset AND section wasn't created in this row
                         skipped += 1

                    processed_count += 1

                # If any errors occurred during processing, you might want to rollback.
                # Currently, it saves valid entries and reports errors.
                # if errors: raise Exception("Import errors occurred.")


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
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


class SubSectionViewSet(viewsets.ModelViewSet):
    """API endpoint for SubSections."""
    queryset = SubSection.objects.select_related('section__depot').prefetch_related('assets').all().order_by('section__name', 'name')
    serializer_class = SubSectionSerializer
    permission_classes = [permissions.AllowAny]
    # Add filtering capability
    filterset_fields = ['section']


class AssetViewSet(viewsets.ModelViewSet):
    """API endpoint for Assets."""
    queryset = Asset.objects.select_related('subsection__section__depot').all().order_by('subsection__name', 'name')
    serializer_class = AssetSerializer
    permission_classes = [permissions.AllowAny]
    # Add filtering capability
    filterset_fields = ['subsection']
