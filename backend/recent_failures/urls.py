# Path: backend/recent_failures/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecentFailureViewSet

router = DefaultRouter()
router.register(r'', RecentFailureViewSet, basename='recent-failure')

urlpatterns = [
    path('', include(router.urls)),
]