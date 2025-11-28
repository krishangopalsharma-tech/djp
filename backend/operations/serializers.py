# Path: backend/operations/serializers.py
from rest_framework import serializers
from supervisors.models import Supervisor
from .models import SupervisorMovement

class SupervisorMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorMovement
        fields = ['id', 'date', 'supervisor', 'location', 'on_leave', 'leave_from', 'leave_to', 'look_after', 'purpose', 'created_at', 'updated_at']

class SupervisorWithMovementSerializer(serializers.ModelSerializer):
    """
    Serializes a Supervisor and nests their movement for a specific day.
    """
    movement = SupervisorMovementSerializer(read_only=True)
    depot_display = serializers.SerializerMethodField()

    class Meta:
        model = Supervisor
        fields = [
            'id', 'name', 'designation', 'depot_display',
            'movement' # This will be our nested movement data
        ]
    
    def get_depot_display(self, obj):
        if obj.depot:
            return obj.depot.code if obj.depot.code else obj.depot.name
        return None