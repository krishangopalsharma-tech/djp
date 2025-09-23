# Path: backend/failures/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FailureViewSet, FailureAttachmentViewSet

router = DefaultRouter()
# We register the endpoint at the path 'logs' (e.g., /api/v1/failures/logs/)
router.register(r'logs', FailureViewSet, basename='failure')
router.register(r'attachments', FailureAttachmentViewSet, basename='failure-attachment')

urlpatterns = [
    path('', include(router.urls)),
]