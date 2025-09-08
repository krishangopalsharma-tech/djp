# Path: backend/failures/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FailureViewSet

router = DefaultRouter()
# We register the endpoint at the path 'logs' (e.g., /api/v1/failures/logs/)
router.register(r'logs', FailureViewSet, basename='failure')

urlpatterns = [
    path('', include(router.urls)),
]