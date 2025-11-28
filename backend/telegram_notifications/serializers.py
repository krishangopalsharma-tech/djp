# Path: backend/telegram_notifications/serializers.py
from rest_framework import serializers
from .models import TelegramSettings, TelegramGroup

class TelegramSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramSettings
        fields = ['id', 'bot_token']

class TelegramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramGroup
        fields = ['id', 'key', 'name', 'chat_id', 'link']