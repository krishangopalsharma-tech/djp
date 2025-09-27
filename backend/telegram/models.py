from django.db import models
import requests
from django.conf import settings

class TelegramGroup(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True, null=True, blank=True)
    chat_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def send_message(self, message, parse_mode='HTML'):
        """
        Sends a text message to the Telegram group.
        """
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle exceptions for network errors, HTTP errors, etc.
            print(f"Failed to send message to {self.name}: {e}")
            return None

    def send_document(self, document, caption=''):
        """
        Sends a document to the Telegram group.
        'document' should be a file-like object.
        """
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendDocument"
        files = {'document': document}
        payload = {
            'chat_id': self.chat_id,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        try:
            response = requests.post(url, data=payload, files=files)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send document to {self.name}: {e}")
            return None