from django.db import models
from core.models import TimestampedModel
from django.utils import timezone

class FailureIDSettings(TimestampedModel):
    """
    A singleton model to store the configuration for generating Failure IDs.
    """
    RESET_CHOICES = (
        ('yearly', 'Yearly'),
        ('monthly', 'Monthly'),
        ('never', 'Never'),
    )
    
    prefix = models.CharField(max_length=10, default='RF')
    padding_digits = models.PositiveSmallIntegerField(default=4)
    reset_cycle = models.CharField(max_length=10, choices=RESET_CHOICES, default='yearly')
    
    # Internal fields to track the sequence
    last_number = models.PositiveIntegerField(default=0)
    last_reset_date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Failure ID Settings"

    def __str__(self):
        return "Failure ID Configuration"

    def save(self, *args, **kwargs):
        # Enforce singleton pattern
        self.pk = 1
        super(FailureIDSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        # Get or create the single settings object
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
