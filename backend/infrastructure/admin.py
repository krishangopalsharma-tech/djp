# Path: backend/infrastructure/admin.py

from django.contrib import admin
# Add SubSection to the import list
from .models import Depot, Station, Section, SubSection, Circuit, Supervisor

admin.site.register(Depot)
admin.site.register(Station)
admin.site.register(Section)
admin.site.register(SubSection) # Add this line
admin.site.register(Circuit)
admin.site.register(Supervisor)
