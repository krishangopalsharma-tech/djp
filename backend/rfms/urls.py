# Path: backend/rfms/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from core.views import HealthView
from rest_framework.routers import DefaultRouter

# Import all the ViewSets
from depots.views import DepotViewSet, EquipmentViewSet
# --- Import InfrastructureTreeView from sections.views ---
from sections.views import SectionViewSet, SubSectionViewSet, AssetViewSet, InfrastructureTreeView
from stations.views import StationViewSet, StationEquipmentViewSet
from supervisors.views import SupervisorViewSet
from circuits.views import CircuitViewSet
from reports.views import ScheduledReportViewSet
from telegram_notifications.views import TelegramSettingsViewSet, TelegramGroupViewSet
from failure_config.views import FailureIDSettingsViewSet
from users.views import UserViewSet

# --- Main API Router Setup ---
router = DefaultRouter()
router.register(r'depots', DepotViewSet, basename='depot')
router.register(r'equipments', EquipmentViewSet, basename='equipment')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'subsections', SubSectionViewSet, basename='subsection')
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'stations', StationViewSet, basename='station')
router.register(r'station-equipments', StationEquipmentViewSet, basename='stationequipment')
router.register(r'supervisors', SupervisorViewSet, basename='supervisor')
router.register(r'circuits', CircuitViewSet, basename='circuit')
router.register(r'reports', ScheduledReportViewSet, basename='report')
router.register(r'telegram-settings', TelegramSettingsViewSet, basename='telegram-settings')
router.register(r'telegram-groups', TelegramGroupViewSet, basename='telegram-group')
router.register(r'failure-id-settings', FailureIDSettingsViewSet, basename='failureid-settings')
router.register(r'users', UserViewSet, basename='user')
# ... (add other viewsets here as you build them) ...

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- ADD THIS CUSTOM PATH ---
    path("api/v1/infrastructure-tree/", InfrastructureTreeView.as_view(), name="infrastructure-tree"),
    
    # API Routes from the main router
    path("api/v1/", include(router.urls)),

    # Other app-specific non-router includes
    path("api/v1/health/", HealthView.as_view(), name="health"),
    path("api/v1/failures/", include("failures.urls")),
    path("api/v1/email/", include("email_notifications.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/logbook/", include("logbook.urls")),
    path("api/v1/recent-failures/", include("recent_failures.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/operations/", include("operations.urls")),
    path("api/v1/archive/", include("archive.urls")),
]

if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))