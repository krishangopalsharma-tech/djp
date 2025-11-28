# Path: backend/email_notifications/views.py
from rest_framework import viewsets, permissions, response, status
from rest_framework.decorators import action
from django.core.mail import send_mail, get_connection
from django.conf import settings
from .models import EmailSettings
from .serializers import EmailSettingsSerializer

class EmailSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the singleton Email Settings.
    """
    queryset = EmailSettings.objects.all()
    serializer_class = EmailSettingsSerializer
    permission_classes = [permissions.AllowAny] # Use AllowAny for dev

    def get_object(self):
        obj, created = EmailSettings.objects.get_or_create(pk=1)
        return obj

    # --- Standard Singleton Actions ---
    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # A PUT should not be partial by default
        partial = kwargs.pop('partial', False) 
        instance = self.get_object()
        
        data_to_send = request.data.copy()

        # If password is sent as an empty string, pop it and make the update partial
        if 'password' in data_to_send and not data_to_send['password']:
            data_to_send.pop('password')
            partial = True 
        
        serializer = self.get_serializer(instance, data=data_to_send, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # The serializer will handle saving 'recipients' and 'password' (if provided)
        serializer.save() 
        
        data = serializer.data
        if 'password' in data:
            del data['password']
        return response.Response(data)

    # --- Custom Test Action ---
    @action(detail=False, methods=['post'], url_path='test')
    def test_email(self, request):
        to_email = request.data.get('to_email')
        if not to_email:
            return response.Response({'error': 'to_email field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            settings_obj = self.get_object()
            
            # Connection settings (safe for None or empty strings)
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host=settings_obj.host or None,
                port=settings_obj.port or None,
                username=settings_obj.username or None,
                password=settings_obj.password or None,
                use_tls=(settings_obj.encryption == 'STARTTLS'),
                use_ssl=(settings_obj.encryption == 'SSL/TLS')
            )
            
            # --- START OF FIX ---
            # Make from_email formatting safe in case fields are None or empty
            from_name = settings_obj.from_name or ''
            from_addr = settings_obj.from_address or 'rfms@example.com' # Use a fallback
            
            # Ensure from_addr is not empty
            if not from_addr:
                from_addr = 'rfms@example.com'
                
            from_email_string = f"{from_name} <{from_addr}>"
            # --- END OF FIX ---

            send_mail(
                subject='RFMS Test Email',
                message='This is a test email from the RFMS application.',
                from_email=from_email_string, # <-- Use the safe string
                recipient_list=[to_email],
                connection=connection, 
                fail_silently=False,
            )
            return response.Response({'message': f'Test email sent to {to_email}.'})
        except Exception as e:
            return response.Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- Disable unwanted actions ---
    def retrieve(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return response.Response({'error': 'Cannot delete settings.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)