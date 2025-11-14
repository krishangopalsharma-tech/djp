# Path: backend/users/views.py
from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    Provides filtering and searching capabilities.
    """
    queryset = User.objects.all().order_by('first_name', 'last_name')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # TODO: Tighten permissions for production

    # --- Filtering and Searching ---
    filterset_fields = ['role', 'designation', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'designation']