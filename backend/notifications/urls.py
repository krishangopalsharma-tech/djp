from django.urls import path
from .views import EmailSettingsView, TestEmailView

urlpatterns = [
    path('settings/email/', EmailSettingsView.as_view(), name='email-settings'),
    path('settings/email/test/', TestEmailView.as_view(), name='test-email'),
]

