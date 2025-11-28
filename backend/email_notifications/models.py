from django.db import models
from core.models import TimestampedModel

class EmailSettings(TimestampedModel):
    """
    A singleton model to store all email configuration.
    """
    ENCRYPTION_CHOICES = [
        ('None', 'None'),
        ('STARTTLS', 'STARTTLS'),
        ('SSL/TLS', 'SSL/TLS'),
    ]
    
    # Singleton setup: We use pk=1
    host = models.CharField(max_length=255, blank=True)
    port = models.PositiveIntegerField(default=587)
    encryption = models.CharField(max_length=10, choices=ENCRYPTION_CHOICES, default='STARTTLS')
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True, help_text="Password is write-only and not returned in API.")
    from_name = models.CharField(max_length=100, blank=True, default='RFMS Notifications')
    from_address = models.EmailField(blank=True, help_text="e.g., no-reply@example.com")
    
    # Store recipients as a JSON object
    recipients = models.JSONField(default=dict, blank=True, help_text="Default recipients, e.g., {'to': [], 'cc': [], 'bcc': []}")

    class Meta:
        verbose_name_plural = "Email Settings"

    def __str__(self):
        return "Email Server Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton pattern
        self.pk = 1
        super(EmailSettings, self).save(*args, **kwargs)
