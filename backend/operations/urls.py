from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupervisorMovementByDateView, SupervisorMovementViewSet, SendMovementReportView
router = DefaultRouter()

# This path is now for saving/updating/deleting individual records
router.register(r'movements', SupervisorMovementViewSet, basename='supervisormovement')

urlpatterns = [
    # This is our new path for getting the daily list
    path('by-date/', SupervisorMovementByDateView.as_view(), name='movements-by-date'),
    path('send-report/', SendMovementReportView.as_view(), name='send-movement-report'),

    # Include the standard router URLs
    path('', include(router.urls)),
]