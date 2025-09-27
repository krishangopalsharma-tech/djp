# Path: backend/failures/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Import the new view
from .views import FailureViewSet, FailureAttachmentViewSet, FailureAttachmentTelegramView

router = DefaultRouter()
# We register the endpoint at the path 'logs' (e.g., /api/v1/failures/logs/)
router.register(r'logs', FailureViewSet, basename='failure')
router.register(r'attachments', FailureAttachmentViewSet, basename='failure-attachment')

urlpatterns = [
    # Add this new path for the Telegram upload view
    path('attachments/send-to-telegram/', FailureAttachmentTelegramView.as_view(), name='failure-attachment-telegram'),
    
    path('', include(router.urls)),
]