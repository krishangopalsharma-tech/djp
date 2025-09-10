# Path: backend/infrastructure/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepotViewSet,
    StationViewSet,
    SectionViewSet,
    SubSectionViewSet,
    CircuitViewSet,
    SupervisorViewSet,
    SupervisorImportView,
    StationImportView,
    DepotImportView,
    EquipmentViewSet,
    StationEquipmentViewSet,
    SectionImportView
)

router = DefaultRouter()
router.register(r'depots', DepotViewSet, basename='depot')
router.register(r'stations', StationViewSet, basename='station')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'subsections', SubSectionViewSet, basename='subsection')
router.register(r'circuits', CircuitViewSet, basename='circuit')
router.register(r'supervisors', SupervisorViewSet, basename='supervisor')
router.register(r'equipments', EquipmentViewSet, basename='equipment')
router.register(r'station-equipments', StationEquipmentViewSet, basename='station-equipment')


urlpatterns = [
    # Custom import views must come BEFORE the router
    path('supervisors/import/', SupervisorImportView.as_view(), name='supervisor-import'),
    path('stations/import/', StationImportView.as_view(), name='station-import'),
    path('depots/import/', DepotImportView.as_view(), name='depot-import'),
    path('sections/import/', SectionImportView.as_view(), name='section-import'),

    # Router URLs
    path('', include(router.urls)),
]

