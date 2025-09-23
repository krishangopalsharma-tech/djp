from django.contrib import admin
from .models import EmailSettings, TelegramGroup

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'username', 'from_address')

@admin.register(TelegramGroup)
class TelegramGroupAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'chat_id')
    # Make the 'key' field read-only in the admin after creation
    readonly_fields = ('key',)
