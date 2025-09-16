# Path: backend/users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# Define an admin class for our custom User model
class UserAdmin(BaseUserAdmin):
    # Add our custom fields ('role', 'designation') to the admin list display
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'designation')
    
    # Add our custom fields to the filters on the right sidebar
    list_filter = BaseUserAdmin.list_filter + ('role', 'designation')
    
    # Add our custom fields to the edit page for a user
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Info', {'fields': ('role', 'designation')}),
    )

# Register our custom User model with our custom UserAdmin class
admin.site.register(User, UserAdmin)