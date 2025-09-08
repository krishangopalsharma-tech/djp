# Path: backend/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model to allow for future customization.
    Extends Django's built-in AbstractUser.
    """
    # You can add extra profile fields here in the future.
    # For example:
    # designation = models.CharField(max_length=100, blank=True)
    pass

    def __str__(self):
        return self.username