from django.contrib import admin
from .models import EmailSettings

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'username', 'from_address')
