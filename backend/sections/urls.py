# Path: backend/sections/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SectionViewSet, SubSectionViewSet, AssetViewSet, InfrastructureTreeView

router = DefaultRouter()
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'subsections', SubSectionViewSet, basename='subsection')
router.register(r'assets', AssetViewSet, basename='asset')

urlpatterns = [
    path('', include(router.urls)),
    # This path was already added, but ensure it's here
    path('infrastructure-tree/', InfrastructureTreeView.as_view(), name='infrastructure-tree'),
]