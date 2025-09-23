from rest_framework import serializers
from .models import Failure, FailureAttachment
from infrastructure.models import Circuit, Station, Section, SubSection, Supervisor

# Mini-serializers for providing nested details in read-only views
class CircuitNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circuit
        fields = ['id', 'circuit_id', 'name']

class StationNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'name', 'code']

class SectionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name']

class SubSectionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubSection
        fields = ['id', 'name']

class SupervisorNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = ['id', 'name']

class FailureListSerializer(serializers.ModelSerializer):
    """
    Serializer for read-only operations (list/retrieve).
    Displays nested objects for related fields.
    """
    circuit = CircuitNestedSerializer(read_only=True)
    station = StationNestedSerializer(read_only=True)
    section = SectionNestedSerializer(read_only=True)
    sub_section = SubSectionNestedSerializer(read_only=True)
    assigned_to = SupervisorNestedSerializer(read_only=True)

    class Meta:
        model = Failure
        fields = '__all__'

class FailureCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for write operations (create/update).
    Accepts primary keys (IDs) for related fields.
    """
    class Meta:
        model = Failure
        fields = [
            'id', 'fail_id', # <-- Add these two
            'entry_type', 'current_status', 'circuit', 'station',
            'section', 'sub_section', 'assigned_to', 'reported_at',
            'resolved_at', 'remark_fail', 'remark_right'
        ]
        # It's even better to make them read-only like this:
        read_only_fields = ['id', 'fail_id']


class FailureAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.ReadOnlyField(source='uploaded_by.username')
    failure = serializers.PrimaryKeyRelatedField(queryset=Failure.objects.all(), write_only=True)

    class Meta:
        model = FailureAttachment
        fields = ['id', 'file', 'description', 'uploaded_by_username', 'created_at', 'failure']
