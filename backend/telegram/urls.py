from django.urls import path
from .views import TelegramGroupList

urlpatterns = [
    path('groups/', TelegramGroupList.as_view(), name='telegram-group-list'),
]
