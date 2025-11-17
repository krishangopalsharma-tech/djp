# Path: backend/failures/admin.py
from django.contrib import admin
from .models import Failure, FailureAttachment
from django.utils.html import format_html
from django.urls import reverse
from django.conf import settings

@admin.register(Failure)
class FailureAdmin(admin.ModelAdmin):
    list_display = (
        'fail_id', 
        'circuit_link', 
        'station_link', 
        'current_status', 
        'severity', 
        'reported_at', 
        'resolved_at',
        'is_archived'
    )
    list_filter = ('current_status', 'severity', 'section', 'station', 'is_archived')
    search_fields = ('fail_id', 'circuit__circuit_id', 'station__name', 'remark_fail')
    date_hierarchy = 'reported_at'
    
    # Use list_select_related for foreign keys
    list_select_related = ('circuit', 'station', 'section', 'sub_section', 'assigned_to')

    @admin.display(description='Circuit')
    def circuit_link(self, obj):
        if not obj.circuit:
            return "N/A"
        link = reverse("admin:circuits_circuit_change", args=[obj.circuit.id])
        return format_html('<a href="{}">{}</a>', link, obj.circuit.circuit_id)

    @admin.display(description='Station')
    def station_link(self, obj):
        if not obj.station:
            return "N/A"
        link = reverse("admin:stations_station_change", args=[obj.station.id])
        return format_html('<a href="{}">{}</a>', link, obj.station.name)

@admin.register(FailureAttachment)
class FailureAttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'failure_link', 'description', 'file_link', 'uploaded_by')
    list_filter = ('failure__station', 'failure__section')
    search_fields = ('failure__fail_id', 'description')
    list_select_related = ('failure', 'uploaded_by')

    @admin.display(description='Failure')
    def failure_link(self, obj):
        link = reverse("admin:failures_failure_change", args=[obj.failure.id])
        return format_html('<a href="{}">{}</a>', link, obj.failure.fail_id)
    
    @admin.display(description='File')
    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
        return "No file"