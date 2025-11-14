# Path: backend/circuits/models.py
from django.db import models
from core.models import TimestampedModel

class Circuit(TimestampedModel):
    """Represents a circuit that can fail."""
    SEVERITY_CHOICES = (
        ('Minor', 'Minor'),
        ('Major', 'Major'),
        ('Critical', 'Critical'),
    )
    
    circuit_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    related_equipment = models.CharField(max_length=200, blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='Minor')
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['circuit_id']

    def __str__(self):
        return f"{self.circuit_id} ({self.name})"