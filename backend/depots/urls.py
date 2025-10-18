# Path: backend/depots/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepotViewSet, EquipmentViewSet

router = DefaultRouter()
# This will create the endpoints for /depots/
router.register(r'depots', DepotViewSet, basename='depot')
# This will create the endpoints for /equipments/
router.register(r'equipments', EquipmentViewSet, basename='equipment')

urlpatterns = [
    # The router will generate all necessary URLs (e.g., /depots/, /depots/{id}/, /equipments/, etc.)
    path('', include(router.urls)),
]