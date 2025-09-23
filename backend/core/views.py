from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from .models import FailureIDSettings
from .serializers import FailureIDSettingsSerializer

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})

class FailureIDSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing the singleton Failure ID Settings.
    """
    queryset = FailureIDSettings.objects.all()
    serializer_class = FailureIDSettingsSerializer
    permission_classes = [permissions.AllowAny] # Adjust in production

    def get_object(self):
        # Always return the singleton object with pk=1
        obj, created = FailureIDSettings.objects.get_or_create(pk=1)
        return obj

    def list(self, request, *args, **kwargs):
        # The list action should return the single settings object, not a list
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)