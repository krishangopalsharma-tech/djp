# Path: backend/infrastructure/serializers.py

from rest_framework import serializers
from .models import Depot, Station, Section, Circuit, Supervisor

class DepotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depot
        fields = ['id', 'name', 'code', 'location']

class StationSerializer(serializers.ModelSerializer):
    # This adds a read-only field to show the depot's name, which is useful for the frontend.
    depot_name = serializers.CharField(source='depot.name', read_only=True)

    class Meta:
        model = Station
        fields = ['id', 'depot', 'depot_name', 'name', 'code']

class SectionSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(source='depot.name', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'depot', 'depot_name', 'name']

class CircuitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circuit
        fields = ['id', 'circuit_id', 'name', 'related_equipment', 'severity', 'details']

class SupervisorSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(source='depot.name', read_only=True, allow_null=True)

    class Meta:
        model = Supervisor
        fields = ['id', 'user', 'name', 'designation', 'mobile', 'email', 'depot', 'depot_name', 'stations', 'sections']
