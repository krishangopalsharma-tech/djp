# Path: backend/infrastructure/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepotViewSet, StationViewSet, SectionViewSet, CircuitViewSet, SupervisorViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'depots', DepotViewSet, basename='depot')
router.register(r'stations', StationViewSet, basename='station')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'circuits', CircuitViewSet, basename='circuit')
router.register(r'supervisors', SupervisorViewSet, basename='supervisor')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]