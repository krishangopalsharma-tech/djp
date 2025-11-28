# Path: backend/supervisors/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupervisorViewSet

router = DefaultRouter()
router.register(r'supervisors', SupervisorViewSet, basename='supervisor')

urlpatterns = [
    path('', include(router.urls)),
]