from django.contrib import admin
from .models import Supervisor

@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'depot', 'mobile', 'email')
    list_filter = ('depot', 'designation')
    search_fields = ('name', 'mobile', 'email', 'depot__name')
    list_select_related = ('depot', 'user')