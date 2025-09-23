from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
import requests

from .models import EmailSettings, TelegramGroup, TelegramSettings
from .serializers import EmailSettingsSerializer, TelegramGroupSerializer, TelegramSettingsSerializer

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
            return Response({'error': f'Failed to send email: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TelegramGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Telegram group configurations.
    """
    serializer_class = TelegramGroupSerializer
    queryset = TelegramGroup.objects.all().order_by('name')
    permission_classes = [permissions.AllowAny]

class TelegramSettingsViewSet(viewsets.ModelViewSet):
    queryset = TelegramSettings.objects.all()
    serializer_class = TelegramSettingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        obj, created = TelegramSettings.objects.get_or_create(pk=1)
        return obj

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class TestTelegramView(APIView):
    """
    A dedicated view to handle sending a test Telegram message.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            if not group_id:
                return Response({'error': 'Group ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            group = TelegramGroup.objects.get(id=group_id)
            bot_token = TelegramSettings.get_active_settings().bot_token

            if not bot_token:
                return Response({'error': 'Telegram Bot Token is not configured.'}, status=status.HTTP_400_BAD_REQUEST)
            if not group.chat_id:
                return Response({'error': f'Chat ID for "{group.name}" is not configured.'}, status=status.HTTP_400_BAD_REQUEST)

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': group.chat_id,
                'text': f"This is a test message from the RFMS application for the group: {group.name}.",
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
            response_data = response.json()
            if response_data.get('ok'):
                return Response({'message': 'Test message sent successfully.'})
            else:
                error_description = response_data.get('description', 'Unknown error from Telegram.')
                return Response({'error': f'Telegram API Error: {error_description}'}, status=status.HTTP_400_BAD_REQUEST)
        
        except TelegramGroup.DoesNotExist:
            return Response({'error': 'Telegram group not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Network Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            print(f"UNEXPECTED ERROR in TestTelegramView: {e}")
            return Response({'error': f'An unexpected server error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)