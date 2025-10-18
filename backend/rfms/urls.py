# Path: backend/rfms/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from core.views import HealthView

urlpatterns = [
    path("admin/", admin.site.urls),

    # API Routes
    path("api/v1/health/", HealthView.as_view(), name="health"),
    path("api/v1/failure-config/", include("failure_config.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/failures/", include("failures.urls")),
    path("api/v1/reports/", include("reports.urls")),
    path("api/v1/telegram/", include("telegram_notifications.urls")),
    path("api/v1/email/", include("email_notifications.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/logbook/", include("logbook.urls")),
    path("api/v1/recent-failures/", include("recent_failures.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/operations/", include("operations.urls")),
    path("api/v1/sections/", include("sections.urls")),
    path("api/v1/stations/", include("stations.urls")),
    path("api/v1/supervisors/", include("supervisors.urls")),
    path("api/v1/", include("depots.urls")),
    path("api/v1/circuits/", include("circuits.urls")),
    path("api/v1/archive/", include("archive.urls"))
]
if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]