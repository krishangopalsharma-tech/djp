from django.urls import path
from .views import DashboardDataView

urlpatterns = [
    # This URL /api/v1/dashboard/data/ will now work
    path('data/', DashboardDataView.as_view(), name='dashboard-data'),
]