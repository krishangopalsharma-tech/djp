# Path: backend/reports/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
from .models import ScheduledReport
from .serializers import ScheduledReportSerializer

class ScheduledReportViewSet(viewsets.ModelViewSet):
    """API endpoint for Scheduled Reports."""
    queryset = ScheduledReport.objects.all().order_by('name')
    serializer_class = ScheduledReportSerializer
    permission_classes = [permissions.AllowAny] # Dev setting

    @action(detail=True, methods=['post'], url_path='upload_template', parser_classes=[MultiPartParser, FileUploadParser])
    def upload_template(self, request, pk=None):
        """Upload a template file for a specific scheduled report."""
        try:
            report = self.get_object()
        except ScheduledReport.DoesNotExist:
            return Response({'error': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get('template')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # If a template already exists, delete the old one
        if report.template:
            report.template.delete(save=False)

        report.template = file
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from telegram_notifications.models import TelegramGroup
from telegram_notifications.bot import send_telegram_document

class SendReportView(APIView):
    """
    API endpoint to receive generated reports (PDF/Excel) and forward them to the Telegram Reports group.
    """
    parser_classes = [MultiPartParser, FileUploadParser]
    permission_classes = [permissions.AllowAny] # Dev setting

    def post(self, request, format=None):
        files = request.FILES.getlist('files')
        if not files:
            return Response({'error': 'No files provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the "reports" group chat ID
            group = TelegramGroup.objects.get(key='reports')
            chat_id = group.chat_id
            if not chat_id:
                 return Response({'error': 'Reports group has no Chat ID configured.'}, status=status.HTTP_400_BAD_REQUEST)
        except TelegramGroup.DoesNotExist:
            return Response({'error': 'Reports Telegram group not found.'}, status=status.HTTP_404_NOT_FOUND)

        success_count = 0
        errors = []

        for f in files:
            try:
                # f is an InMemoryUploadedFile or TemporaryUploadedFile
                # send_telegram_document expects a file-like object
                # We can pass f.open() or f directly depending on the wrapper, 
                # but usually f acts as a file handle.
                # We need to ensure the cursor is at the beginning if it was read before, 
                # but here it's fresh from the request.
                
                caption = f"📊 Report: {f.name}"
                send_telegram_document(chat_id, f, caption)
                success_count += 1
            except Exception as e:
                errors.append(f"Failed to send {f.name}: {str(e)}")

        if success_count == 0 and errors:
             return Response({'error': 'Failed to send reports.', 'details': errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': f'Successfully sent {success_count} reports.',
            'errors': errors
        }, status=status.HTTP_200_OK)