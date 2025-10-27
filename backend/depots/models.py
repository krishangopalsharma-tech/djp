# Path: backend/depots/models.py
from django.db import models
from core.models import TimestampedModel

class Depot(TimestampedModel):
    """Represents a physical depot or location."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    location = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name

class Equipment(TimestampedModel):
    """Represents a piece of measuring equipment assigned to a depot."""
    depot = models.ForeignKey(Depot, related_name='equipments', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="Measuring Equipment name")
    model_type = models.CharField(max_length=100, blank=True, help_text="Model / Type")
    asset_id = models.CharField(max_length=100, blank=True, help_text="Asset / Serial ID")
    location_in_depot = models.CharField(max_length=150, blank=True, help_text="Location within the Depot")
    notes = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True) # Add quantity field

    def __str__(self):
        return f"{self.name} ({self.depot.name})"