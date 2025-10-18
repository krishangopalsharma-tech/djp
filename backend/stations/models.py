from django.db import models
from core.models import TimestampedModel

class Station(TimestampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    depot = models.ForeignKey('depots.Depot', on_delete=models.CASCADE)

class StationEquipment(TimestampedModel):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
