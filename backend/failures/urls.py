# Path: backend/failures/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FailureViewSet, FailureAttachmentViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'logs', FailureViewSet, basename='failure')
router.register(r'attachments', FailureAttachmentViewSet, basename='failure-attachment')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
