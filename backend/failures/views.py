# Path: backend/failures/views.py

from rest_framework import viewsets, permissions
from .models import Failure
from .serializers import FailureListSerializer, FailureCreateUpdateSerializer

class FailureViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows failures to be viewed or edited.
    """
    # select_related is a performance optimization. It fetches the related
    # objects in a single database query, preventing many extra queries.
    queryset = Failure.objects.select_related(
        'circuit', 'station', 'section', 'sub_section', 'assigned_to'
    ).all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        """
        Choose which serializer to use based on the action.
        - Use FailureCreateUpdateSerializer for creating and updating.
        - Use FailureListSerializer for listing and retrieving.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return FailureCreateUpdateSerializer
        return FailureListSerializer

    # In a future step, we will add logic here to auto-generate the `fail_id`.