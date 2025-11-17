# Path: backend/sections/serializers.py
from rest_framework import serializers
from .models import Section, SubSection, Asset
from depots.models import Depot
from stations.models import Station, StationEquipment # <-- IMPORT Station models

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name', 'quantity', 'unit', 'subsection', 'created_at', 'updated_at']

class SubSectionSerializer(serializers.ModelSerializer):
    assets = AssetSerializer(many=True, read_only=True)
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)

    class Meta:
        model = SubSection
        fields = ['id', 'name', 'section', 'assets', 'asset_count', 'created_at', 'updated_at']

class SectionSerializer(serializers.ModelSerializer):
    subsections = SubSectionSerializer(many=True, read_only=True)
    subsection_count = serializers.IntegerField(source='subsections.count', read_only=True)
    depot_display = serializers.CharField(source='depot.name', read_only=True)
    depot_code = serializers.CharField(source='depot.code', read_only=True) # Added for display
    depot = serializers.PrimaryKeyRelatedField(queryset=Depot.objects.all()) # For writing

    class Meta:
        model = Section
        fields = ['id', 'name', 'depot', 'depot_display', 'depot_code', 'subsections', 'subsection_count', 'created_at', 'updated_at']
        read_only_fields = ['depot_display', 'depot_code']

# --- Serializers for the Infrastructure Tree View ---

class _AssetTreeSerializer(serializers.ModelSerializer):
    """Lightweight Asset serializer for the tree view."""
    class Meta:
        model = Asset
        fields = ['id', 'name']

class _SubSectionTreeSerializer(serializers.ModelSerializer):
    """Lightweight SubSection serializer for the tree view."""
    assets = _AssetTreeSerializer(many=True, read_only=True)
    class Meta:
        model = SubSection
        fields = ['id', 'name', 'assets']

class _SectionTreeSerializer(serializers.ModelSerializer):
    """Lightweight Section serializer for the tree view."""
    subsections = _SubSectionTreeSerializer(many=True, read_only=True)
    class Meta:
        model = Section
        fields = ['id', 'name', 'subsections']

# --- NEW SERIALIZERS FOR STATIONS ---
class _StationEquipmentTreeSerializer(serializers.ModelSerializer):
    """Lightweight Station Equipment serializer for the tree view."""
    class Meta:
        model = StationEquipment
        fields = ['id', 'name']

class _StationTreeSerializer(serializers.ModelSerializer):
    """Lightweight Station serializer for the tree view."""
    equipments = _StationEquipmentTreeSerializer(many=True, read_only=True)
    class Meta:
        model = Station
        fields = ['id', 'name', 'code', 'equipments']
# --- END NEW SERIALIZERS ---

class _DepotTreeSerializer(serializers.ModelSerializer):
    """Lightweight Depot serializer for the tree view."""
    sections = _SectionTreeSerializer(many=True, read_only=True)
    # --- ADD STATIONS TO THE DEPOT TREE ---
    stations = _StationTreeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Depot
        fields = ['id', 'name', 'code', 'sections', 'stations'] # Add 'stations'