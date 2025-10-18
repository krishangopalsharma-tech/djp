from django.db import models
from core.models import TimestampedModel

class TelegramGroup(TimestampedModel):
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    chat_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class TelegramSettings(TimestampedModel):
    bot_token = models.CharField(max_length=100)

    def __str__(self):
        return "Telegram Settings"
