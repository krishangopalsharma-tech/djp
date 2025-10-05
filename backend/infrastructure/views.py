from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import openpyxl
from django.db import transaction
from django.db.models import Count

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
    queryset = Depot.objects.annotate(equipment_count=Count('equipments')).order_by('name')
    serializer_class = DepotSerializer
    permission_classes = [permissions.AllowAny]

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.select_related('depot').annotate(equipment_count=Count('equipments')).order_by('name')
    serializer_class = StationSerializer
    permission_classes = [permissions.AllowAny]

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related('depot').annotate(subsection_count=Count('subsections')).order_by('name')
    serializer_class = SectionSerializer
    permission_classes = [permissions.AllowAny]

class SubSectionViewSet(viewsets.ModelViewSet):
    # This view already had select_related, which is good.
    # We will replace the static queryset with the dynamic get_queryset method.
    serializer_class = SubSectionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Optionally filters the queryset by a `section` query parameter."""
        queryset = SubSection.objects.select_related('section').all().order_by('name')
        section_id = self.request.query_params.get('section')
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        return queryset

# --- NO CHANGES NEEDED FOR THE VIEWS BELOW ---
class EquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Optionally filters the queryset by a `depot` query parameter."""
        queryset = Equipment.objects.select_related('depot').all()
        depot_id = self.request.query_params.get('depot')
        if depot_id:
            queryset = queryset.filter(depot_id=depot_id)
        return queryset

class StationEquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = StationEquipmentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Optionally filters the queryset by a `station` query parameter."""
        queryset = StationEquipment.objects.select_related('station').all()
        station_id = self.request.query_params.get('station')
        if station_id:
            queryset = queryset.filter(station_id=station_id)
        return queryset

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
