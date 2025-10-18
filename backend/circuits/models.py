from django.db import models
from core.models import TimestampedModel

class Circuit(TimestampedModel):
    circuit_id = models.CharField(max_length=100, unique=True)
    # other fields from admin if any
