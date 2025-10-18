from django.db import models
from core.models import TimestampedModel

class Section(TimestampedModel):
    name = models.CharField(max_length=100)
    depot = models.ForeignKey('depots.Depot', on_delete=models.CASCADE)

class SubSection(TimestampedModel):
    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

class Asset(TimestampedModel):
    name = models.CharField(max_length=100)
