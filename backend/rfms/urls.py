# Path: backend/rfms/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # API Routes
    path("api/v1/core/", include("core.urls")), # <-- CORRECTED THIS LINE
    path("api/v1/users/", include("users.urls")),
    path("api/v1/failures/", include("failures.urls")),
    path("api/v1/infrastructure/", include("infrastructure.urls")),
    path("api/v1/reports/", include("reports.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
]
