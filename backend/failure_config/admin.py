from django.contrib import admin
from .models import FailureIDSettings

@admin.register(FailureIDSettings)
class FailureIDSettingsAdmin(admin.ModelAdmin):
    list_display = ('prefix', 'padding_digits', 'reset_cycle')
    def has_add_permission(self, request):
        return not FailureIDSettings.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False