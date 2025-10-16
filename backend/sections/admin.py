from django.contrib import admin
from .models import Section, SubSection, Asset

# Basic registration for the moved models
admin.site.register(Section)
admin.site.register(SubSection)
admin.site.register(Asset)