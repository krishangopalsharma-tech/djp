from django.db import models
from core.models import TimestampedModel

class FailureIDSettings(TimestampedModel):
    prefix = models.CharField(max_length=10)
    padding_digits = models.IntegerField()
    reset_cycle = models.CharField(max_length=10)
