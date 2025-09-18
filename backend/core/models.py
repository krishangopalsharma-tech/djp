from django.db import models
from django.utils import timezone

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class FailureIDSettings(TimestampedModel):
    """
    A singleton model to store system-wide settings for Failure ID generation.
    """
    prefix = models.CharField(max_length=10, default='RF')
    padding_digits = models.PositiveSmallIntegerField(default=4)
    reset_cycle = models.CharField(
        max_length=10,
        choices=[('yearly', 'Yearly'), ('monthly', 'Monthly'), ('never', 'Never')],
        default='yearly'
    )
    last_number = models.PositiveIntegerField(default=0)
    last_reset_date = models.DateField(default=timezone.now)

    def __str__(self):
        return "Failure ID Generation Settings"

    class Meta:
        verbose_name_plural = "Failure ID Settings"

    @classmethod
    def get_active_settings(cls):
        """
        Gets the single settings object, creating it if it doesn't exist.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

