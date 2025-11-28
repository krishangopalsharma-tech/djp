from django.contrib import admin
from .models import ScheduledReport

@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'frequency',
        'time',
        'send_email',
        'send_telegram',
        'template'
    )
    list_filter = ('frequency', 'send_email', 'send_telegram')
    search_fields = ('name',)
