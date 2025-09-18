# Path: backend/core/serializers.py

from rest_framework import serializers
from .models import FailureIDSettings

class FailureIDSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureIDSettings
        fields = ['id', 'prefix', 'padding', 'reset_cycle']

