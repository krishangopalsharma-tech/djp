from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailSettingsViewSet

# This router is registered under the /api/v1/email/ prefix
router = DefaultRouter()
router.register(r'settings/email', EmailSettingsViewSet, basename='email-settings')

urlpatterns = [
    path('', include(router.urls)),
]