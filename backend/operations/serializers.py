from rest_framework import serializers
from infrastructure.models import Supervisor
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
    depot_name = serializers.CharField(source='depot.name', read_only=True, allow_null=True)

    class Meta:
        model = Supervisor
        fields = [
            'id', 'name', 'designation', 'depot_name',
            'movement' # This will be our nested movement data
        ]
