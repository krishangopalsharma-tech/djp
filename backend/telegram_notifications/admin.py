# Path: backend/telegram_notifications/admin.py
from django.contrib import admin
from .models import TelegramGroup, TelegramSettings

@admin.register(TelegramGroup)
class TelegramGroupAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'chat_id')
    readonly_fields = () # Make 'key' editable

@admin.register(TelegramSettings)
class TelegramSettingsAdmin(admin.ModelAdmin):
    pass