from django.db import models

class Shift(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Morning, Evening, Night")
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

    class Meta:
        ordering = ['start_time']
