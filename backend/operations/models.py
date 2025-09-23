from django.db import models
from core.models import TimestampedModel
from infrastructure.models import Supervisor

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
    purpose = models.TextField(blank=True)
    

    def __str__(self):
        return f"{self.supervisor.name} - {self.date}"