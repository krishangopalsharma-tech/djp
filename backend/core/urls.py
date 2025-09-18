from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthView, FailureIDSettingsViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'failure-id-settings', FailureIDSettingsViewSet, basename='failure-id-settings')

urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
    path("", include(router.urls)), # Include the router's URLs
]

