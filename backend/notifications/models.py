from django.db import models
from core.models import TimestampedModel
from django.core.mail.backends.smtp import EmailBackend

# Create your models here.
class EmailSettings(TimestampedModel):
    # SMTP Server Settings
    host = models.CharField(max_length=255, blank=True)
    port = models.PositiveIntegerField(default=587)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    
    ENCRYPTION_CHOICES = [
        ('STARTTLS', 'STARTTLS'),
        ('SSL/TLS', 'SSL/TLS'),
        ('None', 'None'),
    ]
    encryption = models.CharField(max_length=10, choices=ENCRYPTION_CHOICES, default='STARTTLS')
    
    # Sender Information
    from_name = models.CharField(max_length=255, default='RFMS Notifications')
    from_address = models.EmailField(blank=True)

    # Default Recipients (stored as comma-separated strings)
    to_recipients = models.TextField(blank=True, help_text="Comma-separated list of TO email addresses.")
    cc_recipients = models.TextField(blank=True, help_text="Comma-separated list of CC email addresses.")
    bcc_recipients = models.TextField(blank=True, help_text="Comma-separated list of BCC email addresses.")

    def __str__(self):
        return f"Email Settings for {self.host or 'Not Configured'}"
    
    def get_connection(self):
        """
        Creates and returns an SMTP EmailBackend instance based on stored settings.
        """
        print(f"--- CREATING CONNECTION: Host={self.host}, Port={self.port}, Encryption={self.encryption} ---")
        use_tls = False
        use_ssl = False
        
        if self.encryption == 'STARTTLS':
            use_tls = True
        elif self.encryption == 'SSL/TLS':
            use_ssl = True

        return EmailBackend(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            fail_silently=False
        )
        
    class Meta:
        verbose_name_plural = "Email Settings"


class TelegramGroup(TimestampedModel):
    """
    Stores configuration for a single Telegram group.
    """
    key = models.CharField(max_length=50, unique=True, help_text="A unique key for the group, e.g., 'alerts', 'reports'.")
    name = models.CharField(max_length=100, help_text="A user-friendly name for the group, e.g., 'Alert Group'.")
    chat_id = models.CharField(max_length=100, blank=True, help_text="The unique Chat ID for the Telegram group.")
    link = models.URLField(blank=True, help_text="An optional invitation link or note for the group.")

    def __str__(self):
        return self.name

