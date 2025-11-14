# Path: backend/logbook/urls.py
from django.urls import path
from .views import LogbookDataView

urlpatterns = [
    # This URL /api/v1/logbook/data/ will now work
    path('data/', LogbookDataView.as_view(), name='logbook-data'),
]