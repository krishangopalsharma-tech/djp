# Path: backend/failures/serializers.py
from rest_framework import serializers
from .models import Failure, FailureAttachment
from circuits.models import Circuit
from stations.models import Station
from sections.models import Section, SubSection
from users.models import User
from circuits.serializers import CircuitSerializer
from stations.serializers import StationSerializer
from sections.serializers import SectionSerializer, SubSectionSerializer
from users.serializers import UserSerializer

class FailureAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureAttachment
        fields = '__all__'

class FailureSerializer(serializers.ModelSerializer):
    # Use nested serializers for read-only relationships
    circuit = CircuitSerializer(read_only=True)
    station = StationSerializer(read_only=True)
    section = SectionSerializer(read_only=True)
    sub_section = SubSectionSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    
    # --- START OF FIX ---
    # The queryset for each field was incorrectly nested.
    
    circuit_id = serializers.PrimaryKeyRelatedField(
        queryset=Circuit.objects.all(), # <-- FIXED
        source='circuit', write_only=True, allow_null=True, required=False
    )
    station_id = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(), # <-- FIXED
        source='station', write_only=True, allow_null=True, required=False
    )
    section_id = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(), # <-- FIXED
        source='section', write_only=True, allow_null=True, required=False
    )
    sub_section_id = serializers.PrimaryKeyRelatedField(
        queryset=SubSection.objects.all(), # <-- FIXED
        source='sub_section', write_only=True, allow_null=True, required=False
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), # <-- FIXED
        source='assigned_to', write_only=True, allow_null=True, required=False
    )
    # --- END OF FIX ---

    class Meta:
        model = Failure
        fields = [
            'id', 'fail_id', 'entry_type', 'severity', 'current_status',
            'reported_at', 'resolved_at', 'remark_fail', 'remark_right',
            'was_notified', 'is_archived', 'archived_at', 'archived_reason',
            
            # Read-only nested objects
            'circuit', 'station', 'section', 'sub_section', 'assigned_to',
            
            # Write-only ID fields
            'circuit_id', 'station_id', 'section_id', 'sub_section_id', 'assigned_to_id',
        ]
        read_only_fields = ['fail_id', 'is_archived', 'archived_at']