# Path: backend/telegram_notifications/views.py
from rest_framework import viewsets, permissions, response, status
from rest_framework.decorators import action
from .models import TelegramSettings, TelegramGroup
from .serializers import TelegramSettingsSerializer, TelegramGroupSerializer
from .bot import send_telegram_message # <-- ADD THIS IMPORT

class TelegramSettingsViewSet(viewsets.ModelViewSet):
    """Manages the singleton Telegram Bot settings."""
    queryset = TelegramSettings.objects.all()
    serializer_class = TelegramSettingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if not TelegramSettings.objects.exists():
            TelegramSettings.objects.create(pk=1) # Ensure singleton exists
        return TelegramSettings.objects.all()

    # Add list/retrieve to always return the singleton
    def list(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

class TelegramGroupViewSet(viewsets.ModelViewSet):
    """Manages Telegram Groups for notifications."""
    queryset = TelegramGroup.objects.all().order_by('name')
    serializer_class = TelegramGroupSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        """
        Ensure the default groups (alerts, reports, operations) exist
        before listing.
        """
        expected_groups = [
            {'key': 'alerts', 'name': 'Alerts (Failures & Notifications)'},
            {'key': 'reports', 'name': 'Reports (Scheduled)'},
            {'key': 'operations', 'name': 'Operations (Movements)'},
        ]
        
        for group_def in expected_groups:
            TelegramGroup.objects.get_or_create(
                key=group_def['key'],
                defaults={'name': group_def['name']}
            )
        
        # Now, call the original list method
        return super().list(request, *args, **kwargs)

    # --- ADD THIS ACTION ---
    @action(detail=True, methods=['post'], url_path='send-test-message')
    def send_test_message(self, request, pk=None):
        """Sends a test message to this group."""
        try:
            group = self.get_object()
        except TelegramGroup.DoesNotExist:
            return response.Response({'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not group.chat_id:
            return response.Response({'error': 'This group has no Chat ID configured.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # --- REPLACE SIMULATION WITH REAL CODE ---
            test_text = f"This is a test message from RFMS for the group: <b>{group.name}</b>"
            send_telegram_message(chat_id=group.chat_id, text=test_text)
            # --- END OF REPLACEMENT ---
            
            return response.Response({'message': f"Test message sent to '{group.name}' successfully."})

        except Exception as e:
            # The exception from send_telegram_message will be caught here
            return response.Response({'error': f'Failed to send message: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)