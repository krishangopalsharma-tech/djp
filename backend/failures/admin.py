from django.contrib import admin
from .models import Failure, FailureAttachment

@admin.register(Failure)
class FailureAdmin(admin.ModelAdmin):
    list_display = ('fail_id', 'circuit', 'station', 'current_status', 'severity', 'reported_at', 'resolved_at')
    list_filter = ('current_status', 'severity', 'section', 'station')
    search_fields = ('fail_id', 'circuit__circuit_id', 'station__name', 'remark_fail')
    date_hierarchy = 'reported_at'

    # This is the critical optimization for the admin panel's performance
    list_select_related = ('circuit', 'station', 'section', 'sub_section', 'assigned_to')

admin.site.register(FailureAttachment)