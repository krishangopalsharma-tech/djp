from django.db import models
from core.models import TimestampedModel

def attachment_upload_path(instance, filename):
    return f'attachments/failures/{instance.failure.fail_id}/{filename}'

class Failure(TimestampedModel):
    fail_id = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique Failure ID, auto-generated.")
    entry_type = models.CharField(max_length=10, choices=[('item', 'Item'), ('message', 'Message'), ('warning', 'Warning'), ('major', 'Major'), ('critical', 'Critical')], default='item')
    severity = models.CharField(max_length=10, choices=[('Minor', 'Minor'), ('Major', 'Major'), ('Critical', 'Critical')], default='Minor')
    current_status = models.CharField(max_length=20, choices=[('Draft', 'Draft'), ('Active', 'Active'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved'), ('On Hold', 'On Hold'), ('Information', 'Information')], default='Active')
    reported_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    remark_fail = models.TextField(blank=True, help_text="Initial notes about the failure.")
    remark_right = models.TextField(blank=True, help_text="Notes on how the failure was resolved.")
    was_notified = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_reason = models.TextField(blank=True)
    # Foreign Keys
    circuit = models.ForeignKey('circuits.Circuit', on_delete=models.CASCADE, null=True, blank=True)
    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey('sections.Section', on_delete=models.CASCADE, null=True, blank=True)
    sub_section = models.ForeignKey('sections.SubSection', on_delete=models.CASCADE, null=True, blank=True)
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)


class FailureAttachment(TimestampedModel):
    failure = models.ForeignKey(Failure, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=attachment_upload_path)
    description = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
