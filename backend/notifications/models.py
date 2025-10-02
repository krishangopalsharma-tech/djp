import requests
import json
import html
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

    def send_message(self, message):
        """
        Sends a message to this specific Telegram group using Markdown format.
        """
        bot_token = TelegramSettings.get_active_settings().bot_token
        if not self.chat_id or not bot_token:
            print(f"Warning: Telegram not configured for group '{self.name}' or bot token is missing.")
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_details = e.response.text if e.response else str(e)
            print(f"Error sending Telegram message to {self.name}: {error_details}")
            raise e

    def send_document(self, file_object, filename, caption):
        """
        Sends a document/file to this specific Telegram group.
        """
        bot_token = TelegramSettings.get_active_settings().bot_token
        if not self.chat_id or not bot_token:
            print(f"Warning: Telegram not configured for group '{self.name}' or bot token is missing.")
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        files = {'document': (filename, file_object)}
        data = {
            'chat_id': self.chat_id,
            'caption': html.unescape(caption), # <-- Add html.unescape() here
            'parse_mode': 'HTML'
        }

        # --- ADD THESE TWO LINES FOR DEBUGGING ---
        print("--- Sending Telegram Document ---")
        print(f"PAYLOAD: {data}")
        # -----------------------------------------

        try:
            # Increased timeout for file uploads
            response = requests.post(url, data=data, files=files, timeout=30)
            response.raise_for_status() # This will raise an error for 4xx/5xx responses
        except requests.exceptions.RequestException as e:
            # Log the full error for better debugging
            print(f"Error sending Telegram document to {self.name}: {e}")
            if e.response is not None:
                print(f"Telegram API Response: {e.response.text}")
            raise e

    @staticmethod
    def edit_message_text(chat_id, message_id, new_text):
        """
        A static method to edit the text of an existing message and remove its keyboard.
        """
        bot_token = TelegramSettings.get_active_settings().bot_token
        if not chat_id or not bot_token:
            print("Cannot edit message, missing chat_id or bot_token.")
            return

        url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': new_text,
            'parse_mode': 'Markdown',
            'reply_markup': json.dumps({'inline_keyboard': []}) # This removes the buttons
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_details = e.response.text if e.response else str(e)
            print(f"Error editing Telegram message: {error_details}")


class TelegramSettings(TimestampedModel):
    """A singleton model to store the Telegram Bot Token."""
    bot_token = models.CharField(max_length=255, blank=True, help_text="The HTTP API token for your Telegram Bot.")

    def __str__(self):
        return "Telegram Bot Settings"

    @classmethod
    def get_active_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name_plural = "Telegram Settings"
