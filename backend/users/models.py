# Path: backend/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    'username' stores the unique Employee PF Number.
    """
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        'PF Number',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Represents the unique Employee PF Number.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that PF Number already exists.",
        },
    )

    # --- Custom Fields ---
    ROLE_CHOICES = (
        ('viewer', 'Viewer'),
        ('operator', 'Operator'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='viewer',
        help_text="Defines the user's access level and permissions."
    )
    designation = models.CharField(
        max_length=100, 
        blank=True,
        help_text="The user's job title or designation (e.g., 'Signal Maintainer')."
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        help_text="Contact phone number for the user, used for SMS notifications."
    )
      
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"