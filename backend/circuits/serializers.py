# Path: backend/circuits/serializers.py
from rest_framework import serializers
from .models import Circuit

class CircuitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circuit
        fields = ['id', 'circuit_id', 'name', 'related_equipment', 'severity', 'details', 'created_at', 'updated_at']