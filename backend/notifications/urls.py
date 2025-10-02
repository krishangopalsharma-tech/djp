from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmailSettingsView, 
    TelegramGroupViewSet, 
    TestEmailView, 
    TestTelegramView, 
    TelegramSettingsViewSet
)

router = DefaultRouter()
router.register(r'telegram-groups', TelegramGroupViewSet, basename='telegramgroup')
router.register(r'settings/telegram', TelegramSettingsViewSet, basename='telegram-settings')

urlpatterns = [
    # Existing paths
    path('settings/email/', EmailSettingsView.as_view(), name='email-settings'),
    path('settings/email/test/', TestEmailView.as_view(), name='test-email'),
    path('telegram-groups/test/', TestTelegramView.as_view(), name='test-telegram'),
    path('', include(router.urls)),
]