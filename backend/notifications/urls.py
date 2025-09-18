from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailSettingsView, TelegramGroupViewSet, TestEmailView, TestTelegramView

# Create a router and register our new Telegram viewset with it.
router = DefaultRouter()
router.register(r'telegram-groups', TelegramGroupViewSet, basename='telegramgroup')

urlpatterns = [
    # Path for the singleton EmailSettings
    path('settings/email/', EmailSettingsView.as_view(), name='email-settings'),
    # Path for the test email action, now pointing to its own view
    path('settings/email/test/', TestEmailView.as_view(), name='test-email'),
    # Path for the test telegram action
    path('telegram-groups/test/', TestTelegramView.as_view(), name='test-telegram'),
    # Include the router URLs for Telegram groups
    path('', include(router.urls)),
]

