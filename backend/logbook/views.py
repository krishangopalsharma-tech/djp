# Path: backend/logbook/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from failures.models import Failure
from failures.serializers import FailureSerializer
from django.utils.dateparse import parse_datetime

class LogbookDataView(APIView):
    """
    Provides paginated, filtered, and sorted data for the main logbook.
    """
    permission_classes = [permissions.AllowAny] # Use AllowAny for dev
    serializer_class = FailureSerializer

    def get(self, request, *args, **kwargs):
        # 1. Base Queryset (non-archived failures)
        queryset = Failure.objects.filter(is_archived=False).select_related(
            'circuit', 'station', 'section', 'sub_section', 'assigned_to'
        )

        # 2. Filtering
        params = request.query_params
        
        # General text query
        query_str = params.get('query')
        if query_str:
            queryset = queryset.filter(
                Q(fail_id__icontains=query_str) |
                Q(circuit__circuit_id__icontains=query_str) |
                Q(circuit__name__icontains=query_str) |
                Q(station__name__icontains=query_str) |
                Q(station__code__icontains=query_str) |
                Q(section__name__icontains=query_str) |
                Q(assigned_to__name__icontains=query_str) |
                Q(remark_fail__icontains=query_str) |
                Q(remark_right__icontains=query_str)
            )

        # Multi-select list filters
        circuits = params.getlist('circuits[]')
        if circuits: queryset = queryset.filter(circuit__id__in=circuits)
        
        sections = params.getlist('sections[]')
        if sections: queryset = queryset.filter(section__id__in=sections)
        
        stations = params.getlist('stations[]')
        if stations: queryset = queryset.filter(station__id__in=stations)
        
        supervisors = params.getlist('supervisors[]')
        if supervisors: queryset = queryset.filter(assigned_to__id__in=supervisors)
        
        statuses = params.getlist('statuses[]')
        if statuses: queryset = queryset.filter(current_status__in=statuses)

        # Date range filters (if added later)
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        if date_from:
            dt_from = parse_datetime(date_from)
            if dt_from: queryset = queryset.filter(reported_at__gte=dt_from)
        if date_to:
            dt_to = parse_datetime(date_to)
            if dt_to: queryset = queryset.filter(reported_at__lte=dt_to)

        # 3. Sorting
        sort_key = params.get('sortKey', '-reported_at') # Default sort
        sort_dir = params.get('sortDir', 'desc')
        
        # Map frontend key to backend model field
        sort_field_map = {
            'reported_at': 'reported_at',
            'resolved_at': 'resolved_at',
            'fail_id': 'fail_id',
            'circuit': 'circuit__circuit_id',
            'station': 'station__name',
            'section': 'section__name',
            'assigned_to': 'assigned_to__name',
            'current_status': 'current_status',
        }
        
        sort_field = sort_field_map.get(sort_key, 'reported_at')
        
        # Add descending prefix if needed
        if sort_dir == 'desc':
            sort_field = f"-{sort_field}"
            
        queryset = queryset.order_by(sort_field)

        # 4. Pagination
        page = params.get('page', 1)
        rows_per_page = params.get('rowsPerPage', 20)
        
        paginator = Paginator(queryset, rows_per_page)
        try:
            paginated_failures = paginator.page(page)
        except PageNotAnInteger:
            paginated_failures = paginator.page(1)
        except EmptyPage:
            paginated_failures = paginator.page(paginator.num_pages)

        # 5. Serialization
        serializer = self.serializer_class(paginated_failures, many=True)
        
        return Response({
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'results': serializer.data
        })