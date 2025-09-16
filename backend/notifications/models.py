# Path: backend/notifications/models.py

from django.db import models
from django.core.mail import get_connection
from core.models import TimestampedModel

class EmailSettings(TimestampedModel):
    # Singleton model to store email settings
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=587)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    from_name = models.CharField(max_length=100, default='RFMS Notifications')
    from_address = models.EmailField(default='no-reply@rfms.com')
    
    ENCRYPTION_CHOICES = [
        ('None', 'None'),
        ('STARTTLS', 'STARTTLS'),
        ('SSL/TLS', 'SSL/TLS'),
    ]
    encryption = models.CharField(max_length=10, choices=ENCRYPTION_CHOICES, default='STARTTLS')
    
    # Recipient lists (stored as comma-separated strings)
    default_to = models.TextField(blank=True, help_text="Comma-separated list of default 'To' recipients.")
    default_cc = models.TextField(blank=True, help_text="Comma-separated list of default 'CC' recipients.")
    default_bcc = models.TextField(blank=True, help_text="Comma-separated list of default 'BCC' recipients.")

    def save(self, *args, **kwargs):
        # Enforce a single instance of settings
        self.pk = 1
        super(EmailSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        # Convenience method to get the singleton instance
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def get_connection(self):
        """Creates and returns an email backend connection."""
        # Correctly set use_tls and use_ssl based on the encryption choice
        use_tls = self.encryption == 'STARTTLS'
        use_ssl = self.encryption == 'SSL/TLS'
        
        return get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            fail_silently=False,
        )

    def __str__(self):
        return f"Email Settings for {self.host}"

    class Meta:
        verbose_name_plural = "Email Settings"

