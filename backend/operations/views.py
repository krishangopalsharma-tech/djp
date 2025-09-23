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
from xml.sax.saxutils import escape

def generate_movement_report_pdf(target_date, movements):
    """
    Generates a PDF report for supervisor movements and returns it as a file-like object.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title = f"Supervisor Movement Report for {target_date.strftime('%d-%b-%Y')}"
    elements.append(Paragraph(title, styles['h1']))
    elements.append(Spacer(1, 12))

    # --- CHANGE 2: Add "Sr. No." and split "Details" into "Location" and "Purpose" ---
    data = [['Sr. No.', 'Supervisor', 'Designation', 'Status', 'Location', 'Purpose / Details']]
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]

    for i, m in enumerate(movements):
        row_index = i + 1
        
        # --- CHANGE 3: Populate the new columns based on status ---
        status_text = "On Leave" if m.on_leave else "On Duty"
        location_text = ""
        purpose_details = []

        if m.on_leave:
            location_text = "N/A"
            date_range = "N/A"
            if m.leave_from and m.leave_to:
                date_range = f"{m.leave_from.strftime('%d-%b')} to {m.leave_to.strftime('%d-%b')}"
            purpose_details.append(f"Duration: {escape(date_range)}")
            if m.look_after:
                purpose_details.append(f"Looked After By: {escape(m.look_after.name)}")
        else:
            location_text = escape(m.location)
            if m.purpose:
                purpose_details.append(escape(m.purpose))

        data.append([
            str(row_index),  # Serial number
            Paragraph(m.supervisor.name, styles['BodyText']),
            Paragraph(m.supervisor.depot.name if m.supervisor.depot else 'N/A', styles['BodyText']),
            Paragraph(status_text, styles['BodyText']),
            Paragraph(location_text, styles['BodyText']),
            Paragraph("<br/>".join(purpose_details), styles['BodyText']),
        ])
        
        if m.on_leave:
            style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), colors.lightpink))

    # --- CHANGE 2 (cont.): Update column widths for the new layout ---
    table = Table(data, colWidths=[40, 110, 80, 60, 100, 140])
    table.setStyle(TableStyle(style_commands))
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Unchanged views
class SupervisorMovementByDateView(APIView):
    # This class is unchanged
    pass

class SupervisorMovementViewSet(viewsets.ModelViewSet):
    # This class is unchanged
    pass

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

        # --- CHANGE 1: Add sorting by depot name, then by supervisor name ---
        movements = SupervisorMovement.objects.filter(date=target_date).select_related(
            'supervisor__depot', 
            'look_after'
        ).order_by('supervisor__depot__name', 'supervisor__name')

        pdf_buffer = generate_movement_report_pdf(target_date, movements)
        pdf_filename = f"Movement_Report_{target_date.strftime('%Y-%m-%d')}.pdf"
        
        caption = f"Supervisor Movement Report for {target_date.strftime('%d-%b-%Y')}"
        
        try:
            groups_to_send = ['alert', 'reports']
            for group_key in groups_to_send:
                tg_group = TelegramGroup.objects.get(key=group_key)
                tg_group.send_document(pdf_buffer, pdf_filename, caption)
                pdf_buffer.seek(0)

            return Response({"status": "Report PDF sent successfully"}, status=status.HTTP_200_OK)
        except TelegramGroup.DoesNotExist:
            return Response({"error": "A required Telegram group (alert or reports) is not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Failed to send Telegram document: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)