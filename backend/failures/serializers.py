from rest_framework import serializers
from .models import Failure, FailureAttachment
# Import the newly optimized serializers
from infrastructure.serializers import (
    CircuitSerializer, StationSerializer, SectionSerializer, SubSectionSerializer, SupervisorSerializer
)

class FailureListSerializer(serializers.ModelSerializer):
    """
    Serializer for read-only operations (list/retrieve).
    Displays optimized nested objects for related fields.
    """
    circuit = CircuitSerializer(read_only=True)
    station = StationSerializer(read_only=True)
    section = SectionSerializer(read_only=True)
    sub_section = SubSectionSerializer(read_only=True)
    assigned_to = SupervisorSerializer(read_only=True)

    class Meta:
        model = Failure
        # Explicitly define fields to prevent errors with old migration data
        fields = [
            'id', 'fail_id', 'entry_type', 'severity', 'current_status',
            'circuit', 'station', 'section', 'sub_section', 'assigned_to',
            'reported_at', 'resolved_at', 'remark_fail', 'remark_right',
            'was_notified', 'is_archived', 'archived_at', 'archived_reason',
            'created_at', 'updated_at'
        ]

class FailureCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for write operations (create/update).
    """
    class Meta:
        model = Failure
        fields = [
            'id', 'fail_id',
            'entry_type', 'current_status', 'circuit', 'station',
            'section', 'sub_section', 'assigned_to', 'reported_at',
            'resolved_at', 'remark_fail', 'remark_right', 'was_notified'
        ]
        read_only_fields = ['id', 'fail_id']

class FailureAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.ReadOnlyField(source='uploaded_by.username')
    failure = serializers.PrimaryKeyRelatedField(queryset=Failure.objects.all(), write_only=True)

    class Meta:
        model = FailureAttachment
        fields = ['id', 'file', 'description', 'uploaded_by_username', 'created_at', 'failure']