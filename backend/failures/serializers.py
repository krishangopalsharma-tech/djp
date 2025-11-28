# Path: backend/failures/serializers.py
from rest_framework import serializers
from .models import Failure, FailureAttachment
from circuits.models import Circuit
from stations.models import Station
from sections.models import Section, SubSection
from users.models import User
from supervisors.models import Supervisor
from circuits.serializers import CircuitSerializer
from stations.serializers import StationSerializer
from sections.serializers import SectionSerializer, SubSectionSerializer
from users.serializers import UserSerializer
from supervisors.serializers import SupervisorSerializer

class FailureAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureAttachment
        fields = '__all__'
        read_only_fields = ['telegram_file_id', 'telegram_message_id']

class FailureSerializer(serializers.ModelSerializer):
    # Read-only nested objects for display
    circuit = CircuitSerializer(read_only=True)
    station = StationSerializer(read_only=True)
    section = SectionSerializer(read_only=True)
    sub_section = SubSectionSerializer(read_only=True)
    assigned_to = SupervisorSerializer(read_only=True)
    
    # Calculated field
    duration_minutes = serializers.SerializerMethodField()
    
    # Write-only ID fields (Crucial for saving data)
    circuit_id = serializers.PrimaryKeyRelatedField(
        queryset=Circuit.objects.all(),
        source='circuit', write_only=True, allow_null=True, required=False
    )
    station_id = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
        source='station', write_only=True, allow_null=True, required=False
    )
    section_id = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(),
        source='section', write_only=True, allow_null=True, required=False
    )
    sub_section_id = serializers.PrimaryKeyRelatedField(
        queryset=SubSection.objects.all(),
        source='sub_section', write_only=True, allow_null=True, required=False
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=Supervisor.objects.all(), 
        source='assigned_to', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Failure
        fields = [
            'id', 'fail_id', 'entry_type', 'severity', 'current_status',
            'reported_at', 'resolved_at', 'remark_fail', 'remark_right',
            'was_notified', 'is_archived', 'archived_at', 'archived_reason',
            'duration_minutes',
            
            # Read-only nested objects
            'circuit', 'station', 'section', 'sub_section', 'assigned_to',
            
            # Write-only ID fields
            'circuit_id', 'station_id', 'section_id', 'sub_section_id', 'assigned_to_id',
        ]
        read_only_fields = ['fail_id', 'is_archived', 'archived_at']

    # --- THIS METHOD MUST BE INDENTED INSIDE THE CLASS ---
    def get_duration_minutes(self, obj):
        if obj.reported_at and obj.resolved_at:
            diff = obj.resolved_at - obj.reported_at
            return int(diff.total_seconds() // 60)
        return None