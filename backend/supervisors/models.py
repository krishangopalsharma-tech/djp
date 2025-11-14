# Path: backend/supervisors/models.py
from django.db import models
from core.models import TimestampedModel
from depots.models import Depot
from sections.models import Section, SubSection, Asset # Import SubSection and Asset
from stations.models import Station
from django.conf import settings

class Supervisor(TimestampedModel):
    """Represents a supervisor, usually associated with a depot."""
    depot = models.ForeignKey(Depot, related_name='supervisors', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Link to a Django user account if applicable."
    )

    # --- INFRASTRUCTURE ASSIGNMENTS ---
    stations = models.ManyToManyField(Station, blank=True, related_name='supervisors')
    sections = models.ManyToManyField(Section, blank=True, related_name='supervisors')
    
    # --- ADD THESE TWO LINES ---
    subsections = models.ManyToManyField(SubSection, blank=True, related_name='supervisors')
    assets = models.ManyToManyField(Asset, blank=True, related_name='supervisors')
    # --- END OF ADDITION ---

    class Meta:
        ordering = ['depot__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.designation})"