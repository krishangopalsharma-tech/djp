from django.db import models
from core.models import TimestampedModel

class EmailSettings(TimestampedModel):
    host = models.CharField(max_length=100)
    port = models.IntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    from_address = models.EmailField()
