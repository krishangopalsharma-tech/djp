# Path: backend/failure_config/serializers.py
from rest_framework import serializers
from .models import FailureIDSettings

class FailureIDSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureIDSettings
        # Expose only the fields the user can configure
        fields = ['id', 'prefix', 'padding_digits', 'reset_cycle']