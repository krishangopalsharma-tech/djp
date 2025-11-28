# Path: backend/telegram_notifications/models.py
from django.db import models
from core.models import TimestampedModel

class TelegramSettings(TimestampedModel):
    # This is a singleton model
    bot_token = models.CharField(max_length=255, blank=True, help_text="The HTTP API token for your Telegram Bot.")
    
    class Meta:
        verbose_name_plural = "Telegram Settings"
    
    def __str__(self):
        return "Telegram Bot Settings"

class TelegramGroup(TimestampedModel):
    key = models.CharField(max_length=50, unique=True, help_text="A unique key for the group, e.g., 'alerts', 'reports'.")
    name = models.CharField(max_length=100, help_text="A user-friendly name for the group.")
    chat_id = models.CharField(max_length=100, blank=True, help_text="The unique Chat ID for the Telegram group.")
    link = models.URLField(blank=True, help_text="An optional invitation link.")
    
    def __str__(self):
        return self.name