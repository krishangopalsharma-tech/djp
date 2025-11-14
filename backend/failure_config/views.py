# Path: backend/failure_config/views.py
from rest_framework import viewsets, permissions, response, status
from .models import FailureIDSettings
from .serializers import FailureIDSettingsSerializer

class FailureIDSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the singleton Failure ID Settings.
    """
    queryset = FailureIDSettings.objects.all()
    serializer_class = FailureIDSettingsSerializer
    permission_classes = [permissions.AllowAny] # Dev setting

    def get_object(self):
        # Always return the singleton object (pk=1), creating it if it doesn't exist.
        obj, created = FailureIDSettings.objects.get_or_create(pk=1)
        return obj

    def list(self, request, *args, **kwargs):
        # The list action should just return the single object
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # Retrieve action also returns the single object
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Don't allow creating new objects, always update the existing one
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Don't allow deleting the singleton object
        return response.Response(
            {'error': 'This object cannot be deleted.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )