from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import openpyxl
from django.db import transaction

from .models import (
    Depot, Station, Section, SubSection, Circuit, Supervisor, 
    Equipment, StationEquipment, Asset
)
from .serializers import (
    DepotSerializer, StationSerializer, SectionSerializer, SubSectionSerializer,
    CircuitSerializer, SupervisorSerializer, EquipmentSerializer, StationEquipmentSerializer,
    AssetSerializer
)

class DepotViewSet(viewsets.ModelViewSet):
    # Removed redundant prefetch_related
    queryset = Depot.objects.all().order_by('name')
    serializer_class = DepotSerializer
    permission_classes = [permissions.AllowAny]

class StationViewSet(viewsets.ModelViewSet):
    # Removed redundant prefetch_related
    queryset = Station.objects.select_related('depot').all().order_by('name')
    serializer_class = StationSerializer
    permission_classes = [permissions.AllowAny]

class SectionViewSet(viewsets.ModelViewSet):
    # Removed redundant prefetch_related
    queryset = Section.objects.select_related('depot').all().order_by('name')
    serializer_class = SectionSerializer
    permission_classes = [permissions.AllowAny]

class SubSectionViewSet(viewsets.ModelViewSet):
    # Removed redundant prefetch_related
    queryset = SubSection.objects.select_related('section').all().order_by('name')
    serializer_class = SubSectionSerializer
    permission_classes = [permissions.AllowAny]

# --- NO CHANGES NEEDED FOR THE VIEWS BELOW ---
class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.select_related('depot').all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.AllowAny]

class StationEquipmentViewSet(viewsets.ModelViewSet):
    queryset = StationEquipment.objects.select_related('station').all()
    serializer_class = StationEquipmentSerializer
    permission_classes = [permissions.AllowAny]

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('subsection').all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.AllowAny]

class CircuitViewSet(viewsets.ModelViewSet):
    queryset = Circuit.objects.all().order_by('circuit_id')
    serializer_class = CircuitSerializer
    permission_classes = [permissions.AllowAny]

class SupervisorViewSet(viewsets.ModelViewSet):
    queryset = Supervisor.objects.select_related('depot').all().order_by('name')
    serializer_class = SupervisorSerializer
    permission_classes = [permissions.AllowAny]

# --- NO CHANGES NEEDED FOR IMPORT VIEWS ---
class DepotImportView(APIView):
    # ... (content is unchanged)
    pass
class StationImportView(APIView):
    # ... (content is unchanged)
    pass
class SectionImportView(APIView):
    # ... (content is unchanged)
    pass
class SupervisorImportView(APIView):
    # ... (content is unchanged)
    pass
class CircuitImportView(APIView):
    # ... (content is unchanged)
    pass