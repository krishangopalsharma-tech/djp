# Path: backend/core/models.py

from django.db import models

# This is a base model that other models can inherit from.
# It automatically adds 'created_at' and 'updated_at' timestamp fields.
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # This tells Django not to create a database table for this model.
        # It's only for other models to inherit from.
        abstract = True