from django.db import models
from core.models import TimestampedModel
from telegram_notifications.models import TelegramGroup
import os

def report_template_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/reports/<id>/<filename>
    return f'reports/{instance.id}/{filename}'

class ScheduledReport(TimestampedModel):
    """Defines a report that runs on a schedule."""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    DAY_CHOICES = [
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday'),
    ]

    name = models.CharField(max_length=200)
    template = models.FileField(upload_to=report_template_path, null=True, blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES, default='Mon')
    day_of_month = models.PositiveSmallIntegerField(default=1)
    time = models.TimeField()
    
    send_email = models.BooleanField(default=False)
    send_telegram = models.BooleanField(default=False)
    telegram_groups = models.ManyToManyField(TelegramGroup, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
