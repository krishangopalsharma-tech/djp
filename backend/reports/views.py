from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import ScheduledReport
from .serializers import ScheduledReportSerializer

class ScheduledReportViewSet(viewsets.ModelViewSet):
    queryset = ScheduledReport.objects.all().order_by('name')
    serializer_class = ScheduledReportSerializer
    permission_classes = [permissions.AllowAny] # Adjust in production

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def upload_template(self, request, pk=None):
        report = self.get_object()
        file_obj = request.FILES.get('template')
        if not file_obj:
            return Response({'error': 'No template file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        report.template = file_obj
        report.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
