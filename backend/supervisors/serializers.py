# Path: backend/supervisors/serializers.py
from rest_framework import serializers
from .models import Supervisor
from depots.models import Depot
# Import the models we need to link
from sections.models import SubSection, Asset, Section
from stations.models import Station, StationEquipment # Import StationEquipment

class SupervisorSerializer(serializers.ModelSerializer):
    depot_display = serializers.CharField(source='depot.name', read_only=True)
    depot = serializers.PrimaryKeyRelatedField(queryset=Depot.objects.all(), allow_null=True, required=False)
    
    # Add fields for managing assignments
    stations = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(), many=True, required=False)
    sections = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all(), many=True, required=False)
    subsections = serializers.PrimaryKeyRelatedField(queryset=SubSection.objects.all(), many=True, required=False)
    assets = serializers.PrimaryKeyRelatedField(queryset=Asset.objects.all(), many=True, required=False)
    station_equipments = serializers.PrimaryKeyRelatedField(queryset=StationEquipment.objects.all(), many=True, required=False)

    class Meta:
        model = Supervisor
        fields = [
            'id', 'name', 'designation', 'mobile', 'email', 'depot', 'depot_display', 'user', 
            'stations', 'sections', 'subsections', 'assets', 'station_equipments', # Add new fields
            'created_at', 'updated_at'
        ]
        read_only_fields = ['depot_display']

    def update(self, instance, validated_data):
        # M2M fields must be set after the instance is saved
        stations_data = validated_data.pop('stations', None)
        sections_data = validated_data.pop('sections', None)
        subsections_data = validated_data.pop('subsections', None)
        assets_data = validated_data.pop('assets', None)
        station_equipments_data = validated_data.pop('station_equipments', None)
        
        # Update the supervisor instance
        instance = super().update(instance, validated_data)
        
        # Now update the M2M relationships
        if stations_data is not None:
            instance.stations.set(stations_data)
        if sections_data is not None:
            instance.sections.set(sections_data)
        if subsections_data is not None:
            instance.subsections.set(subsections_data)
        if assets_data is not None:
            instance.assets.set(assets_data)
        if station_equipments_data is not None:
            instance.station_equipments.set(station_equipments_data)
            
        return instance