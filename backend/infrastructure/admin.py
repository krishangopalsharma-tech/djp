# Path: backend/infrastructure/admin.py

from django.contrib import admin
# Add SubSection to the import list
from .models import Depot, Station, Section, SubSection, Circuit, Supervisor, Equipment, StationEquipment

class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 1 # Show one extra blank row for adding new equipment

@admin.register(Depot)
class DepotAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location')
    inlines = [EquipmentInline]

class StationEquipmentInline(admin.TabularInline):
    model = StationEquipment
    extra = 1 # Show one extra blank row for adding

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'depot')
    list_filter = ('depot', 'category')
    search_fields = ('name', 'code', 'depot__name', 'category')
    inlines = [StationEquipmentInline]


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'depot', 'mobile', 'email')
    list_filter = ('depot', 'designation')
    search_fields = ('name', 'mobile', 'email', 'depot__name')

admin.site.register(Section)
admin.site.register(SubSection) # Add this line
admin.site.register(Circuit)
admin.site.register(Equipment)
admin.site.register(StationEquipment)

