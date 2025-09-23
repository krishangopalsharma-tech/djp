from django.db import models
from core.models import TimestampedModel
from notifications.models import TelegramGroup # Make sure to import TelegramGroup

# Helper function for report template uploads
def report_template_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/report_templates/<id>_<filename>
    return f'report_templates/{instance.id}_{filename}'

class ScheduledReport(TimestampedModel):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    DAY_OF_WEEK_CHOICES = [
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
    ]

    name = models.CharField(max_length=200)
    template = models.FileField(upload_to=report_template_path, blank=True, null=True)

    # Schedule fields
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    day_of_week = models.CharField(max_length=3, choices=DAY_OF_WEEK_CHOICES, default='Mon')
    day_of_month = models.PositiveSmallIntegerField(default=1)
    time = models.TimeField()

    # Delivery options
    send_email = models.BooleanField(default=False)
    send_telegram = models.BooleanField(default=False)

    # UPDATED: Changed from ForeignKey to ManyToManyField
    telegram_groups = models.ManyToManyField(TelegramGroup, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
