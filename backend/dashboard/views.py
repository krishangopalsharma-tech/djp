# Path: backend/dashboard/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db import models
from django.db.models import Count, Avg, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from failures.models import Failure
from sections.models import Section

class DashboardDataView(APIView):
    """
    API endpoint to provide aggregated data for the dashboard.
    """
    permission_classes = [permissions.AllowAny] # Use AllowAny for dev

    def get(self, request, *args, **kwargs):
        # 1. Get Filters
        range_key = request.query_params.get('range', '30d')
        section_ids = request.query_params.getlist('sections[]')

        # 2. Determine Time Range
        now = timezone.now()
        start_date = now
        if range_key == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif range_key == '7d':
            start_date = now - timedelta(days=7)
        else: # Default to 30d
            start_date = now - timedelta(days=30)

        # 3. Base Queryset
        base_qs = Failure.objects.filter(is_archived=False, reported_at__gte=start_date)
        if section_ids:
            base_qs = base_qs.filter(section__id__in=section_ids)

        # 4. Calculate KPIs
        active_failures = base_qs.filter(current_status__in=['Active', 'In Progress', 'On Hold']).count()
        resolved_in_range = base_qs.filter(current_status='Resolved').count()
        critical_alerts = base_qs.filter(severity='Critical').count()
        
        resolved_failures = base_qs.filter(current_status='Resolved', resolved_at__isnull=False)
        duration_avg = resolved_failures.aggregate(
            avg_duration=Avg(F('resolved_at') - F('reported_at'))
        )['avg_duration']
        
        avg_resolution_time = 'N/A'
        if duration_avg:
            total_seconds = duration_avg.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            avg_resolution_time = f"{hours}h {minutes}m"

        kpis = {
            'active_failures': active_failures,
            'resolved_in_range': resolved_in_range,
            'avg_resolution_time': avg_resolution_time,
            'critical_alerts': critical_alerts,
        }

        # 5. Chart: Status by Section
        status_by_section = base_qs.values('section__name').annotate(
            active=Count('id', filter=models.Q(current_status='Active')),
            resolved=Count('id', filter=models.Q(current_status='Resolved')),
        ).order_by('-active')

        # 6. Chart: Resolved over Time
        resolved_over_time = base_qs.filter(current_status='Resolved').annotate(
            date=TruncDate('resolved_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        
        # 7. Compile Response
        data = {
            'kpis': kpis,
            'charts': {
                'status_by_section': list(status_by_section),
                'resolved_over_time': list(resolved_over_time),
            }
        }
        
        return Response(data)