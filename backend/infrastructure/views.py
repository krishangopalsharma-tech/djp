# Path: backend/infrastructure/views.py

from rest_framework import viewsets, permissions
from .models import Depot, Station, Section, Circuit, Supervisor
from .serializers import (
    DepotSerializer,
    StationSerializer,
    SectionSerializer,
    CircuitSerializer,
    SupervisorSerializer
)

class DepotViewSet(viewsets.ModelViewSet):
    queryset = Depot.objects.all().order_by('name')
    serializer_class = DepotSerializer
    # Temporarily allow any request for development purposes.
    # We will secure this again after implementing frontend login.
    permission_classes = [permissions.AllowAny] # <-- CHANGE THIS

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.select_related('depot').all().order_by('name')
    serializer_class = StationSerializer
    permission_classes = [permissions.AllowAny] # <-- CHANGE THIS

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related('depot').all().order_by('name')
    serializer_class = SectionSerializer
    permission_classes = [permissions.AllowAny] # <-- CHANGE THIS

class CircuitViewSet(viewsets.ModelViewSet):
    queryset = Circuit.objects.all().order_by('circuit_id')
    serializer_class = CircuitSerializer
    permission_classes = [permissions.AllowAny] # <-- CHANGE THIS

class SupervisorViewSet(viewsets.ModelViewSet):
    queryset = Supervisor.objects.select_related('depot').all().order_by('name')
    serializer_class = SupervisorSerializer
    permission_classes = [permissions.AllowAny] # <-- CHANGE THIS