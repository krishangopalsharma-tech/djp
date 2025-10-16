from django.contrib import admin
from .models import Depot, Equipment

class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 1

@admin.register(Depot)
class DepotAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location')
    inlines = [EquipmentInline]

admin.site.register(Equipment)