from django.db import models
from core.models import TimestampedModel
from depots.models import Depot

class Supervisor(TimestampedModel):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, null=True, blank=True
    )
    designation = models.CharField(max_length=100, blank=True)
    depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name