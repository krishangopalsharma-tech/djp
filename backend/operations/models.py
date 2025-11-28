# Path: backend/operations/models.py
from django.db import models
from core.models import TimestampedModel
from supervisors.models import Supervisor

class SupervisorMovement(TimestampedModel):
    date = models.DateField()
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    location = models.CharField(max_length=200, blank=True)
    on_leave = models.BooleanField(default=False)
    leave_from = models.DateField(null=True, blank=True)
    leave_to = models.DateField(null=True, blank=True)
    look_after = models.ForeignKey(
        Supervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='looking_after_assignments'
    )
    # --- FIELD CHANGE ---
    purpose = models.CharField(max_length=100, blank=True) # Was TextField
    
    # --- ADD META CLASS ---
    class Meta:
        ordering = ['-date', 'supervisor__name']
        unique_together = ('date', 'supervisor') # Ensure one entry per supervisor per day

    def __str__(self):
        return f"{self.supervisor.name} - {self.date}"