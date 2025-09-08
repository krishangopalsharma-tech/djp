# Path: backend/failures/admin.py

from django.contrib import admin
from .models import Failure

@admin.register(Failure)
class FailureAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('fail_id', 'circuit', 'station', 'current_status', 'severity', 'reported_at', 'resolved_at')
    # Filters on the right sidebar
    list_filter = ('current_status', 'severity', 'section', 'station')
    # Search bar fields
    search_fields = ('fail_id', 'circuit__circuit_id', 'station__name', 'remark_fail')
    # Date hierarchy navigation
    date_hierarchy = 'reported_at'