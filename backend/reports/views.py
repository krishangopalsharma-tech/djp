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