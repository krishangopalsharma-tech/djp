# Path: backend/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Customized admin view for the User model."""
    
    # Add custom fields to the list display
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff', 
        'role', 'designation', 'phone_number'
    )
    
    # Add custom fields to the filters
    list_filter = BaseUserAdmin.list_filter + ('role', 'designation')
    
    # Add custom fields to the user editing page (fieldsets)
    # This adds a new section called 'Custom Info' to the user admin page
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Info', {'fields': ('role', 'designation', 'phone_number')}),
    )
    
    # Add custom fields to the 'add user' form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Info', {'fields': ('role', 'designation', 'phone_number')}),
    )
    
    # Make custom fields searchable
    search_fields = BaseUserAdmin.search_fields + ('role', 'designation', 'phone_number')
