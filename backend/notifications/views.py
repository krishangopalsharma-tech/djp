from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
import requests
from .models import EmailSettings, TelegramGroup
from .serializers import EmailSettingsSerializer, TelegramGroupSerializer

class EmailSettingsView(APIView):
    """
    API view to get or create/update the single EmailSettings object.
    """
    def get(self, request, *args, **kwargs):
        settings, created = EmailSettings.objects.get_or_create(pk=1)
        serializer = EmailSettingsSerializer(settings)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        settings, created = EmailSettings.objects.get_or_create(pk=1)
        serializer = EmailSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestEmailView(APIView):
    """
    A dedicated view to handle sending a test email.
    """
    def post(self, request, *args, **kwargs):
        settings_obj, created = EmailSettings.objects.get_or_create(pk=1)
        
        print(f"--- SENDING TEST EMAIL WITH SETTINGS ---")
        print(f"Host: {settings_obj.host}")
        print(f"Port: {settings_obj.port}")
        print(f"Username: {settings_obj.username}")
        print(f"Encryption: {settings_obj.encryption}")
        print(f"From Address: {settings_obj.from_address}")
        
        if not all([settings_obj.host, settings_obj.username, settings_obj.password, settings_obj.from_address]):
            return Response({'error': 'SMTP server not configured.'}, status=status.HTTP_400_BAD_REQUEST)

        recipient = request.data.get('recipient')
        if not recipient:
            return Response({'error': 'Recipient email is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            connection = settings_obj.get_connection()
            send_mail(
                subject='RFMS Test Email',
                message='This is a test email from the Railway Failure Management System.',
                from_email=settings_obj.from_address,
                recipient_list=[recipient],
                connection=connection,
            )
            return Response({'message': 'Test email sent successfully.'})
        except Exception as e:
            print(f"Email sending failed: {e}")
            return Response({'error': f'Failed to send email: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TelegramGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Telegram group configurations.
    Ensures the three default groups always exist.
    """
    serializer_class = TelegramGroupSerializer

    def get_queryset(self):
        required_keys = {
            'alert': 'Alert Group',
            'files': 'File Upload Group',
            'reports': 'Reports Group'
        }
        
        for key, name in required_keys.items():
            TelegramGroup.objects.get_or_create(key=key, defaults={'name': name})
            
        return TelegramGroup.objects.all().order_by('name')

class TestTelegramView(APIView):
    """
    A dedicated view to handle sending a test Telegram message.
    """
    def post(self, request, *args, **kwargs):
        group_id = request.data.get('group_id')
        if not group_id:
            return Response({'error': 'Group ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = TelegramGroup.objects.get(id=group_id)
        except TelegramGroup.DoesNotExist:
            return Response({'error': 'Telegram group not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not group.chat_id:
            return Response({'error': f'Chat ID for "{group.name}" is not configured.'}, status=status.HTTP_400_BAD_REQUEST)

        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
            return Response({'error': 'Telegram Bot Token is not configured on the server.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': group.chat_id,
            'text': f"This is a test message from the RFMS application for the group: {group.name}.",
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
            
            response_data = response.json()
            if response_data.get('ok'):
                return Response({'message': 'Test message sent successfully.'})
            else:
                # Telegram API returned an error
                error_description = response_data.get('description', 'Unknown error from Telegram.')
                return Response({'error': f'Telegram API Error: {error_description}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except requests.exceptions.RequestException as e:
            return Response({'error': f'Failed to send message: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

