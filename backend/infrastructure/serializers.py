# Path: backend/infrastructure/serializers.py

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
    equipments = EquipmentSerializer(many=True, read_only=True)
    class Meta:
        model = Depot
        fields = ['id', 'name', 'code', 'location', 'equipments']

class StationSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(source='depot.name', read_only=True)
    equipments = StationEquipmentSerializer(many=True, read_only=True)
    class Meta:
        model = Station
        fields = ['id', 'depot', 'depot_name', 'name', 'code', 'category', 'equipments']

class SubSectionSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.name', read_only=True)
    assets = AssetSerializer(many=True, read_only=True)

    class Meta:
        model = SubSection
        fields = ['id', 'section', 'section_name', 'name', 'assets']

class SectionSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(source='depot.name', read_only=True)
    subsections = SubSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'depot', 'depot_name', 'name', 'subsections']

class CircuitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circuit
        fields = ['id', 'circuit_id', 'name', 'related_equipment', 'severity', 'details']

class SupervisorSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(source='depot.name', read_only=True, allow_null=True)

    class Meta:
        model = Supervisor
        fields = ['id', 'user', 'name', 'designation', 'mobile', 'email', 'depot', 'depot_name', 'stations', 'sections']

