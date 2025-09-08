# Path: backend/users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# This will register your custom User model with the Django admin site,
# using the default layout for user management.
admin.site.register(User, UserAdmin)