# Path: backend/failures/models.py

from django.db import models
from django.conf import settings
from core.models import TimestampedModel
from infrastructure.models import Circuit, Station, Section, SubSection, Supervisor

class Failure(TimestampedModel):
    # Choices for fields, matching the frontend
    ENTRY_TYPE_CHOICES = [
        ('item', 'Item'),
        ('message', 'Message'),
        ('warning', 'Warning'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('On Hold', 'On Hold'),
    ]
    SEVERITY_CHOICES = [
        ('Minor', 'Minor'),
        ('Major', 'Major'),
        ('Critical', 'Critical'),
    ]

    # Core Fields
    fail_id = models.CharField(max_length=50, unique=True, help_text="Unique Failure ID, can be auto-generated.")
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES, default='item')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='Minor')
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    # Relational Fields (Links to Infrastructure)
    circuit = models.ForeignKey(Circuit, on_delete=models.PROTECT, related_name="failures")
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True, related_name="failures")
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="failures")
    sub_section = models.ForeignKey(SubSection, on_delete=models.SET_NULL, null=True, blank=True, related_name="failures")
    assigned_to = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name="failures")

    # Time and Remarks
    reported_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    remark_fail = models.TextField(blank=True, help_text="Initial notes about the failure.")
    remark_right = models.TextField(blank=True, help_text="Notes on how the failure was resolved.")

    def __str__(self):
        return self.fail_id

    class Meta:
        ordering = ['-reported_at'] # Show the most recent failures first by default