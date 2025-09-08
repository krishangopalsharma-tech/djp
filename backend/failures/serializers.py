# Path: backend/failures/serializers.py

from rest_framework import serializers
from .models import Failure

class FailureListSerializer(serializers.ModelSerializer):
    """
    Serializer for read-only operations (list/retrieve).
    Displays human-readable names for related fields.
    """
    circuit = serializers.StringRelatedField()
    station = serializers.StringRelatedField()
    section = serializers.StringRelatedField()
    sub_section = serializers.StringRelatedField()
    assigned_to = serializers.StringRelatedField()

    class Meta:
        model = Failure
        fields = '__all__' # Includes all fields from the model


class FailureCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for write operations (create/update).
    Accepts primary keys (IDs) for related fields.
    """
    class Meta:
        model = Failure
        # We list only the fields the frontend is allowed to write.
        # 'fail_id' will be handled automatically on the backend.
        fields = [
            'entry_type', 'severity', 'current_status', 'circuit', 'station',
            'section', 'sub_section', 'assigned_to', 'reported_at',
            'resolved_at', 'remark_fail', 'remark_right'
        ]
