# backend/operations/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from infrastructure.models import Supervisor
from .models import SupervisorMovement
from .serializers import SupervisorMovementSerializer, SupervisorWithMovementSerializer
from datetime import datetime
from notifications.models import TelegramGroup

# Imports for PDF Generation
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_movement_report_pdf(target_date, movements):
    """
    Generates a PDF report for supervisor movements and returns it as a file-like object.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = f"Supervisor Movement Report for {target_date.strftime('%d-%b-%Y')}"
    elements.append(Paragraph(title, styles['h1']))
    elements.append(Spacer(1, 12))

    # Table Data
    data = [['Supervisor', 'Designation', 'Status', 'Details']]
    for m in movements:
        status_text = "On Leave" if m.on_leave else "On Duty"
        details = ""
        if m.on_leave:
            date_range = "N/A"
            if m.leave_from and m.leave_to:
                date_range = f"{m.leave_from.strftime('%d-%b')} to {m.leave_to.strftime('%d-%b')}"
            details = f"Duration: {date_range}"
            if m.look_after:
                details += f"\nLooked After By: {m.look_after.name}"
        else:
            details = f"Location: {m.location}"
            if m.purpose:
                details += f"\nPurpose: {m.purpose}"

        data.append([
            Paragraph(m.supervisor.name, styles['BodyText']),
            Paragraph(m.supervisor.designation, styles['BodyText']),
            Paragraph(status_text, styles['BodyText']),
            Paragraph(details.replace('\n', '&lt;br/&gt;'), styles['BodyText']),
        ])

    # Create and style the table
    table = Table(data, colWidths=[120, 100, 70, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# Unchanged views
class SupervisorMovementByDateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        date_str = request.query_params.get('date', None)
        if not date_str:
            return Response({"error": "A 'date' query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        supervisors = Supervisor.objects.all().order_by('name')
        movements = SupervisorMovement.objects.filter(date=target_date).select_related('supervisor')
        movement_map = {m.supervisor.id: m for m in movements}
        for s in supervisors:
            s.movement = movement_map.get(s.id)
        serializer = SupervisorWithMovementSerializer(supervisors, many=True)
        return Response(serializer.data)

class SupervisorMovementViewSet(viewsets.ModelViewSet):
    queryset = SupervisorMovement.objects.all()
    serializer_class = SupervisorMovementSerializer
    permission_classes = [permissions.AllowAny]


# UPDATED VIEW
class SendMovementReportView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        date_str = request.data.get('date')
        if not date_str:
            return Response({"error": "A 'date' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        movements = SupervisorMovement.objects.filter(date=target_date).select_related('supervisor', 'look_after')

        # 1. Generate the PDF
        pdf_buffer = generate_movement_report_pdf(target_date, movements)
        pdf_filename = f"Movement_Report_{target_date.strftime('%Y-%m-%d')}.pdf"

        # 2. Prepare caption and send to Telegram
        caption = f"Supervisor Movement Report for {target_date.strftime('%d-%b-%Y')}"

        try:
            groups_to_send = ['alert', 'reports']
            for group_key in groups_to_send:
                tg_group = TelegramGroup.objects.get(key=group_key)
                # Use the new send_document method
                tg_group.send_document(pdf_buffer, pdf_filename, caption)
                pdf_buffer.seek(0) # Rewind buffer for the next send

            return Response({"status": "Report PDF sent successfully"}, status=status.HTTP_200_OK)
        except TelegramGroup.DoesNotExist:
            return Response({"error": "A required Telegram group (alert or reports) is not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Failed to send Telegram document: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)