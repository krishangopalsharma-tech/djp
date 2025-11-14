# Path: backend/stations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StationViewSet, StationEquipmentViewSet

router = DefaultRouter()
router.register(r'stations', StationViewSet, basename='station')
router.register(r'station-equipments', StationEquipmentViewSet, basename='stationequipment')

urlpatterns = [
    path('', include(router.urls)),
]