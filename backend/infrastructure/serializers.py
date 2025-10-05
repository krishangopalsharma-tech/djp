from rest_framework import serializers
from .models import (
    Depot, Station, Section, SubSection, Circuit, Supervisor, 
    Equipment, StationEquipment, Asset
)

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'model_type', 'asset_id', 'location_in_depot', 'notes']

class StationEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationEquipment
        fields = '__all__'

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name', 'quantity', 'unit']

class DepotSerializer(serializers.ModelSerializer):
    # This pre-fetches the count, which is much faster than fetching all objects
    equipment_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Depot
        fields = ['id', 'name', 'code', 'location', 'equipment_count']

class StationSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(source='depot.name', read_only=True)
    # This pre-fetches the count, which is much faster
    equipment_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Station
        fields = ['id', 'depot', 'depot_name', 'name', 'code', 'category', 'equipment_count']

class SubSectionSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.name', read_only=True)
    # This pre-fetches the count, which is much faster
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)
    class Meta:
        model = SubSection
        fields = ['id', 'section', 'section_name', 'name', 'asset_count']

class SectionSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(source='depot.name', read_only=True)
    # This pre-fetches the count, which is much faster
    subsection_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Section
        fields = ['id', 'depot', 'depot_name', 'name', 'subsection_count']

class CircuitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circuit
        fields = ['id', 'circuit_id', 'name', 'related_equipment', 'severity', 'details']

class SupervisorSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(source='depot.name', read_only=True, allow_null=True)
    # We remove stations and sections from here to prevent massive queries
    class Meta:
        model = Supervisor
        fields = ['id', 'user', 'name', 'designation', 'mobile', 'email', 'depot', 'depot_name']