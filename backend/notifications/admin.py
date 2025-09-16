# Path: backend/notifications/admin.py

from django.contrib import admin
from .models import EmailSettings

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    # Since it's a singleton, we prevent adding new instances from the admin
    def has_add_permission(self, request):
        return False
    # And we prevent deleting the only instance
    def has_delete_permission(self, request, obj=None):
        return False

