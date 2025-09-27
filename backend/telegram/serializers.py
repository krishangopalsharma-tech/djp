from rest_framework import serializers
from .models import TelegramGroup

class TelegramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramGroup
        fields = '__all__'
