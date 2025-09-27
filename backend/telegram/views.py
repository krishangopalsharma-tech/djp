from rest_framework import generics
from .models import TelegramGroup
from .serializers import TelegramGroupSerializer

class TelegramGroupList(generics.ListAPIView):
    queryset = TelegramGroup.objects.all()
    serializer_class = TelegramGroupSerializer