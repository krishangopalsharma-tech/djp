from django.contrib import admin
from .models import FailureIDSettings

# Register your models here.
@admin.register(FailureIDSettings)
class FailureIDSettingsAdmin(admin.ModelAdmin):
    list_display = ('prefix', 'padding_digits', 'reset_cycle')

    def has_add_permission(self, request):
        # Prevent adding more than one instance
        return not FailureIDSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the instance
        return False
