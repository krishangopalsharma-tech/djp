# Path: backend/depots/serializers.py
from rest_framework import serializers
from .models import Depot, Equipment

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

class DepotSerializer(serializers.ModelSerializer):
    equipments = EquipmentSerializer(many=True, read_only=True)
    equipment_count = serializers.IntegerField(source='equipments.count', read_only=True)

    class Meta:
        model = Depot
        fields = ['id', 'name', 'code', 'location', 'equipments', 'equipment_count', 'created_at', 'updated_at']