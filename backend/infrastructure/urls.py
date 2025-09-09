# Path: backend/infrastructure/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Make sure SubSectionViewSet is imported
from .views import DepotViewSet, StationViewSet, SectionViewSet, SubSectionViewSet, CircuitViewSet, SupervisorViewSet

router = DefaultRouter()
router.register(r'depots', DepotViewSet, basename='depot')
router.register(r'stations', StationViewSet, basename='station')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'subsections', SubSectionViewSet, basename='subsection') # <-- ENSURE THIS LINE EXISTS
router.register(r'circuits', CircuitViewSet, basename='circuit')
router.register(r'supervisors', SupervisorViewSet, basename='supervisor')

urlpatterns = [
    path('', include(router.urls)),
]
