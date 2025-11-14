# Path: backend/reports/serializers.py
from rest_framework import serializers
from .models import ScheduledReport
from telegram_notifications.models import TelegramGroup

class ScheduledReportSerializer(serializers.ModelSerializer):
    # Use 'slug_related_name' to allow setting groups by their 'key' (e.g., 'alerts', 'reports')
    telegram_group_keys = serializers.SlugRelatedField(
        many=True,
        queryset=TelegramGroup.objects.all(),
        slug_field='key',
        source='telegram_groups' # Map to the 'telegram_groups' M2M field
    )
    template_name = serializers.CharField(source='template.name', read_only=True, default=None)

    class Meta:
        model = ScheduledReport
        fields = [
            'id', 'name', 'template', 'template_name', 'frequency', 'day_of_week',
            'day_of_month', 'time', 'send_email', 'send_telegram',
            'telegram_group_keys', 'created_at', 'updated_at'
        ]
        read_only_fields = ['template_name']