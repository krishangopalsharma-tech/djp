# Path: backend/failures/admin.py
from django.contrib import admin
from .models import Failure, FailureAttachment, SmsRecipient

class FailureAttachmentInline(admin.TabularInline):
    """Allows editing attachments directly within the Failure admin page."""
    model = FailureAttachment
    extra = 1  # Number of empty forms to display
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Failure)
class FailureAdmin(admin.ModelAdmin):
    """Customized admin view for the Failure model."""
    list_display = (
        'fail_id', 'station', 'severity', 'current_status', 'reported_at',
        'resolved_at', 'created_by', 'assigned_to'
    )
    list_filter = ('current_status', 'severity', 'section', 'station', 'created_by')
    search_fields = ('fail_id', 'circuit__circuit_id', 'station__name', 'remark_fail')
    date_hierarchy = 'reported_at'
    
    # Fieldsets for better organization in the detail view
    fieldsets = (
        ('Core Information', {
            'fields': ('fail_id', 'entry_type', 'severity', 'current_status', 'reported_at', 'resolved_at')
        }),
        ('Location Details', {
            'fields': ('circuit', 'station', 'section', 'sub_section')
        }),
        ('Assignment and Ownership', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Remarks', {
            'fields': ('remark_fail', 'remark_right')
        }),
        ('Archive Status', {
            'fields': ('is_archived', 'archived_at', 'archived_reason')
        }),
        ('Notification Status', {
            'fields': ('was_notified',)
        }),
    )
    
    readonly_fields = ('fail_id', 'created_at', 'updated_at', 'archived_at')
    inlines = [FailureAttachmentInline]
    
    # Optimize database queries
    list_select_related = ('circuit', 'station', 'section', 'sub_section', 'assigned_to', 'created_by')

@admin.register(FailureAttachment)
class FailureAttachmentAdmin(admin.ModelAdmin):
    """Customized admin view for Failure Attachments."""
    list_display = ('id', 'failure', 'file', 'description', 'uploaded_by', 'created_at')
    list_filter = ('failure__station', 'uploaded_by')
    search_fields = ('description', 'failure__fail_id')
    list_select_related = ('failure', 'uploaded_by')

@admin.register(SmsRecipient)
class SmsRecipientAdmin(admin.ModelAdmin):
    """Admin view for managing SMS recipients."""
    list_display = ('phone_number', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('phone_number',)
