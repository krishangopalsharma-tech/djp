from django_filters import rest_framework as filters
from .models import Failure

class FailureFilter(filters.FilterSet):
    # Support comma-separated status list if needed, or repeated params
    # DRF default for multiple choice is repeated params: ?current_status=Active&current_status=Draft
    current_status = filters.MultipleChoiceFilter(choices=[
        ('Draft', 'Draft'), 
        ('Active', 'Active'), 
        ('In Progress', 'In Progress'), 
        ('Resolved', 'Resolved'), 
        ('On Hold', 'On Hold'), 
        ('Information', 'Information')
    ])
    
    # Range filters
    reported_at = filters.IsoDateTimeFromToRangeFilter() # uses _after and _before usually, OR manual
    # But dashboard sends reported_at__gte.
    # To support explicit lookups like __gte, we can use the dictionary syntax in Meta
    # OR define them explicitly.
    
    # Explicit definition to match "reported_at__gte"
    reported_at__gte = filters.IsoDateTimeFilter(field_name='reported_at', lookup_expr='gte')
    reported_at__lte = filters.IsoDateTimeFilter(field_name='reported_at', lookup_expr='lte')
    
    resolved_at__gte = filters.IsoDateTimeFilter(field_name='resolved_at', lookup_expr='gte')
    resolved_at__lte = filters.IsoDateTimeFilter(field_name='resolved_at', lookup_expr='lte')
    
    # Section by name
    section_name = filters.CharFilter(field_name='section__name', lookup_expr='exact')

    class Meta:
        model = Failure
        fields = ['current_status', 'severity', 'circuit', 'station', 'section', 'assigned_to', 'is_archived']
