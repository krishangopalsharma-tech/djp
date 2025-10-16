from django.contrib import admin
from .models import Station, StationEquipment

class StationEquipmentInline(admin.TabularInline):
    model = StationEquipment
    extra = 1

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'depot')
    list_filter = ('depot', 'category')
    search_fields = ('name', 'code', 'depot__name', 'category')
    inlines = [StationEquipmentInline]

admin.site.register(StationEquipment)