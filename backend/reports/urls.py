from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduledReportViewSet, SendReportView

router = DefaultRouter()
router.register(r'scheduled', ScheduledReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send/', SendReportView.as_view(), name='send-reports'),
]