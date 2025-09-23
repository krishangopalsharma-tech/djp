from rest_framework import serializers
from .models import EmailSettings, TelegramGroup, TelegramSettings

class EmailSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSettings
        fields = '__all__'

class TelegramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramGroup
        fields = ['id', 'key', 'name', 'chat_id', 'link']

class TelegramSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramSettings
        fields = ['id', 'bot_token']
