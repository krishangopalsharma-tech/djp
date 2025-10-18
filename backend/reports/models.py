from django.db import models
from core.models import TimestampedModel

def report_template_path(instance, filename):
    return f'reports/templates/{instance.name}/{filename}'

class ScheduledReport(TimestampedModel):
    name = models.CharField(max_length=200)
    template = models.FileField(upload_to=report_template_path, blank=True, null=True)
    frequency = models.CharField(max_length=10, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='daily')
    day_of_week = models.CharField(max_length=3, choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], default='Mon')
    day_of_month = models.PositiveSmallIntegerField(default=1)
    time = models.TimeField()
    send_email = models.BooleanField(default=False)
    send_telegram = models.BooleanField(default=False)
    telegram_groups = models.ManyToManyField('telegram_notifications.TelegramGroup', blank=True)
