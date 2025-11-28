# Path: backend/reports/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
from .models import ScheduledReport
from .serializers import ScheduledReportSerializer

class ScheduledReportViewSet(viewsets.ModelViewSet):
    """API endpoint for Scheduled Reports."""
    queryset = ScheduledReport.objects.all().order_by('name')
    serializer_class = ScheduledReportSerializer
    permission_classes = [permissions.AllowAny] # Dev setting

    @action(detail=True, methods=['post'], url_path='upload_template', parser_classes=[MultiPartParser, FileUploadParser])
    def upload_template(self, request, pk=None):
        """Upload a template file for a specific scheduled report."""
        try:
            report = self.get_object()
        except ScheduledReport.DoesNotExist:
            return Response({'error': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get('template')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # If a template already exists, delete the old one
        if report.template:
            report.template.delete(save=False)

        report.template = file
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from telegram_notifications.models import TelegramGroup
from telegram_notifications.bot import send_telegram_document

class SendReportView(APIView):
    """
    API endpoint to receive generated reports (PDF/Excel) and forward them to the Telegram Reports group.
    """
    parser_classes = [MultiPartParser, FileUploadParser]
    permission_classes = [permissions.AllowAny] # Dev setting

    def post(self, request, format=None):
        files = request.FILES.getlist('files')
        if not files:
            return Response({'error': 'No files provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the "reports" group chat ID
            group = TelegramGroup.objects.get(key='reports')
            chat_id = group.chat_id
            if not chat_id:
                 return Response({'error': 'Reports group has no Chat ID configured.'}, status=status.HTTP_400_BAD_REQUEST)
        except TelegramGroup.DoesNotExist:
            return Response({'error': 'Reports Telegram group not found.'}, status=status.HTTP_404_NOT_FOUND)

        success_count = 0
        errors = []

        for f in files:
            try:
                # f is an InMemoryUploadedFile or TemporaryUploadedFile
                # send_telegram_document expects a file-like object
                # We can pass f.open() or f directly depending on the wrapper, 
                # but usually f acts as a file handle.
                # We need to ensure the cursor is at the beginning if it was read before, 
                # but here it's fresh from the request.
                
                caption = f"📊 Report: {f.name}"
                send_telegram_document(chat_id, f, caption)
                success_count += 1
            except Exception as e:
                errors.append(f"Failed to send {f.name}: {str(e)}")

        if success_count == 0 and errors:
             return Response({'error': 'Failed to send reports.', 'details': errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': f'Successfully sent {success_count} reports.',
            'errors': errors
        }, status=status.HTTP_200_OK)

from django.db.models import Count, Q
from failures.models import Failure
from depots.models import Depot
from supervisors.models import Supervisor
from stations.models import Station
from sections.models import Section, SubSection, Asset

class OperationalReportView(APIView):
    """
    API endpoint for aggregated operational reports (charts).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Filters
        scope = request.query_params.get('scope') # system, circuit, depot, section, supervisor, subsection, station
        scope_id = request.query_params.get('scope_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        failure_type = request.query_params.get('type') # 'failure', 'event', 'all'

        queryset = Failure.objects.filter(is_archived=False)

        # Apply Scope Filter
        if scope and scope_id:
            # Handle multiple IDs (comma-separated)
            scope_ids = [s for s in scope_id.split(',') if s.strip()]
            
            if scope_ids:
                if scope == 'circuit':
                    queryset = queryset.filter(circuit_id__in=scope_ids)
                elif scope == 'depot':
                    # Failures don't have direct depot FK, usually linked via station or section -> depot
                    queryset = queryset.filter(Q(station__depot_id__in=scope_ids) | Q(section__depot_id__in=scope_ids))
                elif scope == 'section':
                    queryset = queryset.filter(section_id__in=scope_ids)
                elif scope == 'subsection':
                    queryset = queryset.filter(sub_section_id__in=scope_ids)
                elif scope == 'station':
                    queryset = queryset.filter(station_id__in=scope_ids)
                elif scope == 'supervisor':
                    queryset = queryset.filter(assigned_to_id__in=scope_ids)

        # Apply Date Filter
        if start_date:
            queryset = queryset.filter(reported_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(reported_at__date__lte=end_date)

        # Apply Type Filter
        if failure_type and failure_type != 'all':
            # Assuming 'failure' means not 'message' (General Message)
            # Or if you have a specific field. Based on previous work, 'entry_type' distinguishes 'failure' vs 'message'.
            if failure_type == 'failure':
                queryset = queryset.exclude(entry_type='message')
            elif failure_type == 'event': # Assuming 'event' might mean 'message' or something else? 
                # For now, let's assume 'event' is synonymous with 'message' or general logs
                queryset = queryset.filter(entry_type='message')

        # Aggregation for Charts
        status_distribution = queryset.values('current_status').annotate(count=Count('id')).order_by('current_status')
        
        # Type distribution
        type_distribution = queryset.values('entry_type').annotate(count=Count('id')).order_by('entry_type')

        response_data = {
            'status_distribution': status_distribution,
            'type_distribution': type_distribution,
            'total_count': queryset.count()
        }

        # If details are requested (for export)
        if request.query_params.get('details') == 'true':
            from failures.serializers import FailureSerializer
            # Limit to avoid massive payloads, or rely on frontend to handle reasonable ranges
            # For "Reports", usually we want all matching.
            serializer = FailureSerializer(queryset, many=True)
            response_data['failures'] = serializer.data

        return Response(response_data)
        return Response(response_data)

class OperationalExportView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Filters
        scope = request.query_params.get('scope')
        scope_id = request.query_params.get('scope_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        failure_type = request.query_params.get('type')

        queryset = Failure.objects.filter(is_archived=False)

        # Apply Scope Filter
        if scope and scope_id:
            scope_ids = [s for s in scope_id.split(',') if s.strip()]
            if scope_ids:
                if scope == 'circuit':
                    queryset = queryset.filter(circuit_id__in=scope_ids)
                elif scope == 'depot':
                    queryset = queryset.filter(Q(station__depot_id__in=scope_ids) | Q(section__depot_id__in=scope_ids))
                elif scope == 'section':
                    queryset = queryset.filter(section_id__in=scope_ids)
                elif scope == 'subsection':
                    queryset = queryset.filter(sub_section_id__in=scope_ids)
                elif scope == 'station':
                    queryset = queryset.filter(station_id__in=scope_ids)
                elif scope == 'supervisor':
                    queryset = queryset.filter(assigned_to_id__in=scope_ids)

        # Apply Date Filter
        if start_date:
            queryset = queryset.filter(reported_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(reported_at__date__lte=end_date)

        # Apply Type Filter
        if failure_type and failure_type != 'all':
            if failure_type == 'failure':
                queryset = queryset.exclude(entry_type='message')
            elif failure_type == 'event':
                queryset = queryset.filter(entry_type='message')

        from failures.serializers import FailureSerializer
        serializer = FailureSerializer(queryset, many=True)
        return Response(serializer.data)
class InventoryReportView(APIView):
    """
    API endpoint for inventory reports.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, report_type=None):
        if report_type == 'depot_equipment':
            return self.get_depot_equipment(request)
        elif report_type == 'supervisor_assets':
            return self.get_supervisor_assets(request)
        elif report_type == 'station_equipment':
            return self.get_station_equipment(request)
        elif report_type == 'section_assets':
            return self.get_section_assets(request)
        else:
            return Response({'error': 'Invalid report type.'}, status=status.HTTP_400_BAD_REQUEST)

    def get_depot_equipment(self, request):
        depot_ids = request.query_params.getlist('depot_ids[]')
        if not depot_ids:
             depot_ids = request.query_params.getlist('depot_ids') # Try without brackets
        
        queryset = Depot.objects.prefetch_related('stations__equipments').all()
        if depot_ids:
            queryset = queryset.filter(id__in=depot_ids)
        
        data = []
        for depot in queryset:
            # Aggregate equipment count per depot? Or list all equipment?
            # Request says "Report on the availability of measuring equipment."
            # "Filterable by single or multiple depots."
            # Let's list all equipment grouped by depot for now.
            equipments = []
            for station in depot.stations.all():
                for equip in station.equipments.all():
                    equipments.append({
                        'station': station.name,
                        'name': equip.name,
                        'make_modal': equip.make_modal,
                        'quantity': equip.quantity,
                        'status': 'Available' # Placeholder
                    })
            data.append({
                'depot_name': depot.name,
                'equipments': equipments
            })
        return Response(data)

    def get_supervisor_assets(self, request):
        supervisor_id = request.query_params.get('supervisor_id')
        queryset = Supervisor.objects.prefetch_related('assets', 'station_equipments').all()
        
        if supervisor_id:
            queryset = queryset.filter(id=supervisor_id)

        data = []
        for sup in queryset:
            assets = []
            for asset in sup.assets.all():
                assets.append({'type': 'Asset', 'name': asset.name, 'location': str(asset.subsection)})
            for equip in sup.station_equipments.all():
                assets.append({'type': 'Station Equipment', 'name': equip.name, 'location': str(equip.station)})
            
            data.append({
                'name': sup.name,
                'mobile': sup.mobile,
                'assets': assets
            })
        return Response(data)

    def get_station_equipment(self, request):
        station_id = request.query_params.get('station_id')
        queryset = Station.objects.prefetch_related('equipments').all()
        
        if station_id:
            queryset = queryset.filter(id=station_id)
        
        data = []
        for station in queryset:
            equipments = []
            for equip in station.equipments.all():
                equipments.append({
                    'name': equip.name,
                    'make_modal': equip.make_modal,
                    'address': equip.address,
                    'location': equip.location_in_station,
                    'quantity': equip.quantity,
                    'installation_date': equip.installation_date,
                    'codal_life': equip.codal_life
                })
            data.append({
                'station_name': station.name,
                'station_code': station.code,
                'equipments': equipments
            })
        return Response(data)

    def get_section_assets(self, request):
        section_id = request.query_params.get('section_id')
        subsection_id = request.query_params.get('subsection_id')
        
        queryset = Section.objects.prefetch_related('subsections__assets').all()
        
        if section_id:
            queryset = queryset.filter(id=section_id)
        
        data = []
        for section in queryset:
            subsections_data = []
            for sub in section.subsections.all():
                if subsection_id and str(sub.id) != str(subsection_id):
                    continue
                
                assets = []
                for asset in sub.assets.all():
                    assets.append({
                        'name': asset.name,
                        'quantity': asset.quantity,
                        'unit': asset.unit,
                        'installation_date': asset.installation_date,
                        'codal_life': asset.codal_life
                    })
                subsections_data.append({
                    'subsection_name': sub.name,
                    'assets': assets
                })
            
            if subsections_data:
                data.append({
                    'section_name': section.name,
                    'subsections': subsections_data
                })
        return Response(data)