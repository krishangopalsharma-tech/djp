from rest_framework import viewsets
from .models import Shift
from .serializers import ShiftSerializer

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
