from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import EmailSettings
from .serializers import EmailSettingsSerializer
import smtplib

class EmailSettingsView(APIView):
    """
    Retrieve or update the email settings.
    Since there's only one settings object, we don't use a standard ViewSet.
    """
    permission_classes = [permissions.AllowAny] # In production, change to IsAdminUser

    def get(self, request, *args, **kwargs):
        # .first() returns the object or None if it doesn't exist
        settings_obj = EmailSettings.objects.first()
        if not settings_obj:
            # If no settings exist, create a default one
            settings_obj = EmailSettings.objects.create()
        
        serializer = EmailSettingsSerializer(settings_obj)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        settings_obj, _ = EmailSettings.objects.get_or_create(pk=1)
        serializer = EmailSettingsSerializer(settings_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestEmailView(APIView):
    """
    Sends a test email using the saved settings.
    """
    permission_classes = [permissions.AllowAny] # In production, change to IsAdminUser

    def post(self, request, *args, **kwargs):
        to_email = request.data.get('to_email')
        if not to_email:
            return Response({"error": "No recipient email address provided."}, status=status.HTTP_400_BAD_REQUEST)

        settings_obj = EmailSettings.objects.first()
        if not settings_obj or not settings_obj.host:
            return Response({"error": "SMTP settings are not configured."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            send_mail(
                subject='RFMS: Test Email',
                message='This is a test email from the Railway Failure Management System.',
                from_email=f"{settings_obj.from_name} <{settings_obj.from_address}>",
                recipient_list=[to_email],
                fail_silently=False,
                # These settings are configured in Django's core email backend via settings.py
                # but we are overriding them here for this specific call based on DB settings
                connection=settings_obj.get_connection()
            )
            return Response({"message": f"Test email sent successfully to {to_email}."}, status=status.HTTP_200_OK)
        except smtplib.SMTPAuthenticationError as e:
            return Response({"error": f"SMTP Authentication Error: Please check username/password. ({e.smtp_code}: {e.smtp_error.decode()})"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

