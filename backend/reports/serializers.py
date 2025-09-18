from rest_framework import serializers
from .models import ScheduledReport
from notifications.models import TelegramGroup

class ScheduledReportSerializer(serializers.ModelSerializer):
    template_name = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledReport
        fields = [
            'id', 'name', 'template', 'template_name', 'frequency', 'day_of_week',
            'day_of_month', 'time', 'send_email', 'send_telegram',
            'telegram_groups'
        ]
        read_only_fields = ['template'] # Template is handled by a separate upload endpoint

    def get_template_name(self, obj):
        if obj.template:
            return obj.template.name.split('/')[-1] # Return just the filename
        return None