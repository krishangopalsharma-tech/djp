# Path: backend/infrastructure/models.py

from django.db import models
from django.conf import settings

# A common practice is to have a base model for shared fields like timestamps.
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # This makes it a base class, no DB table will be created for it.

class Depot(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name

class Station(TimestampedModel):
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE, related_name="stations")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        unique_together = ('depot', 'name') # A station name should be unique within a depot

    def __str__(self):
        return f"{self.name} ({self.depot.name})"

class Section(TimestampedModel):
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('depot', 'name')

    def __str__(self):
        return self.name

class Circuit(TimestampedModel):
    SEVERITY_CHOICES = [
        ('Minor', 'Minor'),
        ('Major', 'Major'),
        ('Critical', 'Critical'),
    ]
    circuit_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    related_equipment = models.CharField(max_length=200, blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='Minor')
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.circuit_id} ({self.name})"

class Supervisor(TimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Link to a Django user account if applicable."
    )
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, blank=True, related_name="supervisors")
    
    # ManyToManyFields to link a supervisor to multiple stations and sections
    stations = models.ManyToManyField(Station, blank=True)
    sections = models.ManyToManyField(Section, blank=True)

    def __str__(self):
        return self.name

# Add this new class to the file
class SubSection(TimestampedModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="subsections")
    name = models.CharField(max_length=100)

    class Meta:
        # A sub-section name should be unique within its parent section
        unique_together = ('section', 'name')

    def __str__(self):
        return f"{self.name} ({self.section.name})"
