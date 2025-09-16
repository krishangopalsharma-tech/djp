# Path: backend/notifications/serializers.py

from rest_framework import serializers
from .models import EmailSettings

class EmailSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the EmailSettings model.
    """
    class Meta:
        model = EmailSettings
        # Exclude the 'id' field as we'll only ever have one instance
        exclude = ['id']

