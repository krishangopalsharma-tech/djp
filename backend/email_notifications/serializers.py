# Path: backend/email_notifications/serializers.py
from rest_framework import serializers
from .models import EmailSettings

class EmailSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSettings
        fields = [
            'id', 'host', 'port', 'encryption', 'username', 
            'password', 'from_name', 'from_address', 'recipients'
        ]
        extra_kwargs = {
            # Make password write-only (never sent back to frontend)
            'password': {'write_only': True, 'required': False}
        }

    def validate_recipients(self, value):
        # Ensure recipients is a dict with 'to', 'cc', 'bcc' keys
        if not isinstance(value, dict):
            raise serializers.ValidationError("Recipients must be an object.")
        if 'to' not in value: value['to'] = []
        if 'cc' not in value: value['cc'] = []
        if 'bcc' not in value: value['bcc'] = []
        return value