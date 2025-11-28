from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduledReportViewSet, SendReportView, OperationalReportView, InventoryReportView, OperationalExportView

router = DefaultRouter()
router.register(r'scheduled', ScheduledReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send/', SendReportView.as_view(), name='send-report'),
    path('operational/stats/', OperationalReportView.as_view(), name='operational-stats'),
    path('operational/export/', OperationalExportView.as_view(), name='operational-export'),
    path('inventory/<str:report_type>/', InventoryReportView.as_view(), name='inventory-report'),
]