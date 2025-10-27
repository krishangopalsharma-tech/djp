# Path: backend/sections/models.py
from django.db import models
from core.models import TimestampedModel
from depots.models import Depot # Import the Depot model

class Section(TimestampedModel):
    """Represents a section within a depot."""
    depot = models.ForeignKey(Depot, related_name='sections', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('depot', 'name') # Ensure section names are unique within a depot
        ordering = ['depot__name', 'name'] # Default ordering

    def __str__(self):
        depot_code = self.depot.code or self.depot.name
        return f"{self.name} ({depot_code})"

class SubSection(TimestampedModel):
    """Represents a sub-section within a section."""
    section = models.ForeignKey(Section, related_name='subsections', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('section', 'name') # Ensure sub-section names are unique within a section
        ordering = ['section__name', 'name'] # Default ordering

    def __str__(self):
        return f"{self.name} ({self.section.name})"

class Asset(TimestampedModel):
    """Represents an asset within a sub-section."""
    # --- MODIFY THIS LINE ---
    subsection = models.ForeignKey(SubSection, related_name='assets', on_delete=models.CASCADE, null=True) # Add null=True temporarily
    name = models.CharField(max_length=150)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['subsection__name', 'name']

    def __str__(self):
        # Handle case where subsection might be temporarily null during migration
        subsection_name = self.subsection.name if self.subsection else 'No SubSection'
        return f"{self.name} ({subsection_name})"
