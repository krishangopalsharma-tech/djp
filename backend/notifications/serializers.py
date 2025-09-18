from rest_framework import serializers
from .models import EmailSettings, TelegramGroup

class EmailSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSettings
        fields = '__all__'

class TelegramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramGroup
        fields = ['id', 'key', 'name', 'chat_id', 'link']

