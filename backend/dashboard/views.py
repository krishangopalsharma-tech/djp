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
        status_filters = request.query_params.getlist('status[]')

        # 2. Determine Time Range (Start Date)
        now = timezone.now()
        start_date = now
        if range_key == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif range_key == '7d':
            start_date = now - timedelta(days=7)
        else: # Default to 30d
            start_date = now - timedelta(days=30)

        # 3a. Determine Previous Time Range (for trends)
        # today -> yesterday
        # 7d -> prev 7d
        # 30d -> prev 30d
        if range_key == 'today':
            # prev is yesterday
            prev_start_date = start_date - timedelta(days=1)
            prev_end_date = start_date
        elif range_key == '7d':
             prev_start_date = start_date - timedelta(days=7)
             prev_end_date = start_date
        else: # 30d
             prev_start_date = start_date - timedelta(days=30)
             prev_end_date = start_date

        # 3b. Define Contexts
        # Active failures (Reported in range)
        active_qs = Failure.objects.filter(is_archived=False, reported_at__gte=start_date)
        active_prev_qs = Failure.objects.filter(is_archived=False, reported_at__gte=prev_start_date, reported_at__lt=prev_end_date)
        
        # Resolved Failures (Resolved in range)
        resolved_qs = Failure.objects.filter(is_archived=False, resolved_at__gte=start_date)
        resolved_prev_qs = Failure.objects.filter(is_archived=False, resolved_at__gte=prev_start_date, resolved_at__lt=prev_end_date)

        # Apply common filters (Sections)
        if section_ids:
            active_qs = active_qs.filter(section__name__in=section_ids)
            active_prev_qs = active_prev_qs.filter(section__name__in=section_ids)
            resolved_qs = resolved_qs.filter(section__name__in=section_ids)
            resolved_prev_qs = resolved_prev_qs.filter(section__name__in=section_ids)

        # Status filtering (only affects Active counts usually, but let's apply consistent logic)
        if status_filters:
            active_qs = active_qs.filter(current_status__in=status_filters)
            active_prev_qs = active_prev_qs.filter(current_status__in=status_filters)
            if 'Resolved' not in status_filters:
                 resolved_qs = resolved_qs.none()
                 resolved_prev_qs = resolved_prev_qs.none()

        # 4. Calculate KPIs & Trends
        
        # KPI 1: Active Failures (Reported in range)
        active_count = active_qs.filter(current_status__in=['Active', 'In Progress', 'On Hold']).count()
        active_prev_count = active_prev_qs.filter(current_status__in=['Active', 'In Progress', 'On Hold']).count()

        # KPI 2: Resolved Failures (Resolved in range)
        resolved_count = resolved_qs.filter(current_status='Resolved').count()
        resolved_prev_count = resolved_prev_qs.filter(current_status='Resolved').count()

        # KPI 3: Critical Alerts
        # Formula: (Total Active Critical) + (Critical Resolved in Range)
        critical_active_total = Failure.objects.filter(
            is_archived=False, 
            severity='Critical', 
            current_status__in=['Active', 'In Progress', 'On Hold']
        ).count()
        
        critical_resolved_in_range = Failure.objects.filter(
            is_archived=False,
            severity='Critical',
            current_status='Resolved',
            resolved_at__gte=start_date
        ).count()

        critical_count = critical_active_total + critical_resolved_in_range
        
        # Critical Trend: This is tricky because the main metric is a mix of stock and flow.
        # User wants "Compare failure count". 
        # Best proxy: Compare "Criticals Reported in Range" vs "Criticals Reported in Prev Range"
        # OR "Criticals Resolved in Range" vs "Criticals Resolved in Prev Range".
        # Let's use the same formula context but applied to Active Reported? 
        # Actually, let's just use "Criticals Reported" comparison as it indicates INFLOW of criticals.
        critical_reported_current = active_qs.filter(severity='Critical').count()
        critical_reported_prev = active_prev_qs.filter(severity='Critical').count()
        # Ensure we return a number for trend comparison
        critical_trend_val = critical_reported_prev

        # KPI 4: Avg Resolution Time
        avg_resolution_time = 'N/A'
        duration_agg = resolved_qs.filter(current_status='Resolved').aggregate(avg_duration=Avg(F('resolved_at') - F('reported_at')))
        duration_val = duration_agg['avg_duration']
        if duration_val:
            total_seconds = duration_val.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            avg_resolution_time = f"{hours}h {minutes}m"
            
        # Avg Resolution Trend (Prev)
        avg_resolution_time_prev = 'N/A' # Just text for now, or calc?
        # Let's calculate for comparison
        duration_agg_prev = resolved_prev_qs.filter(current_status='Resolved').aggregate(avg_duration=Avg(F('resolved_at') - F('reported_at')))
        duration_val_prev = duration_agg_prev['avg_duration']
        if duration_val_prev:
             total_seconds = duration_val_prev.total_seconds()
             hours = int(total_seconds // 3600)
             minutes = int((total_seconds % 3600) // 60)
             avg_resolution_time_prev = f"{hours}h {minutes}m"

        kpis = {
            'active_failures': active_count,
            'active_prev': active_prev_count,
            
            'resolved_in_range': resolved_count,
            'resolved_prev': resolved_prev_count,
            
            'avg_resolution_time': avg_resolution_time,
            'avg_resolution_time_prev': avg_resolution_time_prev,
            
            'critical_alerts': critical_count,
            'critical_prev_reported': critical_trend_val, # We'll label this "Vs X reported prev"
        }

        # 5. Chart: Status by Section
        # This chart usually shows the CURRENT snapshot or the "Reported in Range" snapshot.
        # Given the "Active" logic above, let's stick to "Reported in Range".
        # We need counts per section.
        
        # Base Chart QS (Sections)
        sections = Section.objects.all()
        if section_ids:
            sections = sections.filter(name__in=section_ids)

        # Annotations
        # We need:
        # - Active/In Progress/On Hold: Based on reported_at >= start_date
        # - Resolved: Based on resolved_at >= start_date (to match KPI)?
        # Mixing time bases in one stacked bar chart is confusing.
        # Usually, a stacked bar chart has a SINGLE time basis (e.g. "Items from this week") OR it is a Snapshot (Current State).
        # Since "Resolve" is a terminal state, "Current State" implies "All time active" + "Recently Resolved".
        # Let's align with the KPIs:
        # Active/IP/Hold = reported >= start
        # Resolved = resolved >= start
        
        filter_active = models.Q(failure__is_archived=False, failure__reported_at__gte=start_date)
        filter_resolved = models.Q(failure__is_archived=False, failure__resolved_at__gte=start_date)
        
        # Apply Status Filter logic
        # If 'Active' is selected in filters, we count it. If not, 0.
        show_active = not status_filters or 'Active' in status_filters
        show_in_progress = not status_filters or 'In Progress' in status_filters
        show_on_hold = not status_filters or 'On Hold' in status_filters
        show_resolved = not status_filters or 'Resolved' in status_filters

        def count_if(condition, show):
            return Count('failure', filter=condition) if show else models.Value(0, output_field=models.IntegerField())

        status_by_section = sections.annotate(
            active=count_if(filter_active & models.Q(failure__current_status='Active'), show_active),
            in_progress=count_if(filter_active & models.Q(failure__current_status='In Progress'), show_in_progress),
            on_hold=count_if(filter_active & models.Q(failure__current_status='On Hold'), show_on_hold),
            resolved=count_if(filter_resolved & models.Q(failure__current_status='Resolved'), show_resolved),
        ).annotate(
            total_activity=F('active') + F('in_progress') + F('on_hold') + F('resolved')
        ).order_by('-total_activity', 'name').values('name', 'active', 'in_progress', 'resolved', 'on_hold')

        # 6. Chart: Resolved over Time
        # MUST use resolved_qs foundation
        resolved_over_time = resolved_qs.filter(current_status='Resolved').annotate(
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