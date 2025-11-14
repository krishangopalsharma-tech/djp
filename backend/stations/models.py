# Path: backend/stations/models.py
from django.db import models
from core.models import TimestampedModel
from depots.models import Depot

class Station(TimestampedModel):
    """Represents a station, associated with a depot."""
    depot = models.ForeignKey(Depot, related_name='stations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    # Ensure code is unique and not nullable (we'll make it non-nullable)
    code = models.CharField(max_length=20, unique=True, null=False, blank=False) # Changed to non-nullable
    category = models.CharField(max_length=100, blank=True)

    class Meta:
        # REMOVE the unique_together constraint
        # unique_together = ('depot', 'name') 
        ordering = ['name'] # Order by name by default

    def __str__(self):
        depot_code = self.depot.code or self.depot.name
        return f"{self.name} ({self.code}) [{depot_code}]"

# ... (StationEquipment model remains the same) ...
class StationEquipment(TimestampedModel):
    station = models.ForeignKey(Station, related_name='equipments', on_delete=models.CASCADE)
    category = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, help_text="Equipment Name")
    make_modal = models.CharField(max_length=100, blank=True, help_text="Make / Model")
    address = models.CharField(max_length=150, blank=True, help_text="e.g., IP Address")
    location_in_station = models.CharField(max_length=150, blank=True, help_text="Physical location in the station")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['station__name', 'name']

    def __str__(self):
        return f"{self.name} at {self.station.name}"