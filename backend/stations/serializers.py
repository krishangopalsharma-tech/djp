# Path: backend/stations/serializers.py
from rest_framework import serializers
from .models import Station, StationEquipment
from depots.models import Depot

class StationEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationEquipment
        # Ensure all fields from the model are included
        fields = ['id', 'station', 'category', 'name', 'make_modal', 'address', 'location_in_station', 'quantity', 'created_at', 'updated_at']

class StationSerializer(serializers.ModelSerializer):
    equipments = StationEquipmentSerializer(many=True, read_only=True)
    equipment_count = serializers.IntegerField(source='equipments.count', read_only=True)
    # Include depot details for display, use PrimaryKeyRelatedField for writing
    depot_display = serializers.CharField(source='depot.name', read_only=True)
    depot = serializers.PrimaryKeyRelatedField(queryset=Depot.objects.all()) # For writing

    class Meta:
        model = Station
        fields = ['id', 'name', 'code', 'category', 'depot', 'depot_display', 'equipments', 'equipment_count', 'created_at', 'updated_at']
        read_only_fields = ['depot_display']