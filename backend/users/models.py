# Path: backend/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator

class User(AbstractUser):
    """
    Custom user model to allow for future customization.
    Extends Django's built-in AbstractUser.
    The 'username' field is used to store the unique Employee PF Number.
    """
    # We override the username field to provide custom help text and error messages.
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Represents the unique Employee PF Number.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that PF Number already exists.",
        },
    )

    ROLE_CHOICES = (
        ('viewer', 'Viewer'),
        ('operator', 'Operator'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    designation = models.CharField(max_length=100, blank=True)
      
    # We are using the built-in first_name and last_name fields for the user's name.

    def __str__(self):
        return self.username
