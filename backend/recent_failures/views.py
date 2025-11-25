# Path: backend/recent_failures/views.py
from rest_framework import viewsets, permissions
from failures.models import Failure
from failures.serializers import FailureSerializer
from django.utils import timezone

class RecentFailureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view the 50 most recent, non-archived failures.
    """
    # Select the 10 most recent failures that are NOT archived
    # Select the 50 most recent failures that are NOT archived and within the last 7 days
    # Select the 50 most recent failures that are NOT archived
    def get_queryset(self):
        return Failure.objects.filter(is_archived=False).select_related(
            'circuit', 'station', 'section', 'assigned_to'
        ).order_by('-reported_at')[:50]
    serializer_class = FailureSerializer
    permission_classes = [permissions.AllowAny] # Use AllowAny for dev