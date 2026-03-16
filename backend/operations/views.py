# Path: backend/operations/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from supervisors.models import Supervisor
from .models import SupervisorMovement
from .serializers import SupervisorMovementSerializer, SupervisorWithMovementSerializer
from datetime import datetime
from telegram_notifications.models import TelegramGroup
from telegram_notifications.bot import send_telegram_document # Import the bot function

import io
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4, landscape

from django.http import FileResponse
from .utils import get_daily_movements_logic

def generate_movement_report_pdf(target_date, supervisors_with_movements):
    """
    Generates a PDF report for supervisor movements and returns it as a file-like object.
    Accepts a list of Supervisor objects with attached .movement attribute.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    title_style = styles['h1']
    title_style.alignment = TA_CENTER

    title = f"Supervisor Movement Report for {target_date.strftime('%d-%b-%Y')}"
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20)) 

    data = [['Sr. No.', 'Depot', 'Supervisor', 'Designation', 'Status', 'Location', 'Purpose / Details']]
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (6, 1), (6, -1), 'LEFT'),
    ]

    body_style_left = ParagraphStyle(name='BodyTextLeft', parent=styles['BodyText'], alignment=TA_LEFT)

    for i, s in enumerate(supervisors_with_movements):
        row_index = i + 1
        m = s.movement 
        
        # Defaults if no movement record
        status_text = "On Duty"
        depot_code = s.depot.code if s.depot and s.depot.code else 'N/A'
        supervisor_name = s.name
        designation = s.designation
        location_text = ""
        details_flowables = []

        if m:
            status_text = "On Leave" if m.on_leave else "On Duty"
            
            if m.on_leave:
                location_text = "N/A"
                date_range = "N/A"
                if m.leave_from and m.leave_to:
                    date_range = f"{m.leave_from.strftime('%d-%b')} to {m.leave_to.strftime('%d-%b')}"
                
                details_flowables.append(Paragraph(f"Duration: {escape(date_range)}", body_style_left))
                if m.look_after:
                    details_flowables.append(Paragraph(f"Looked After By: {escape(m.look_after.name)}", body_style_left))
            else:
                location_text = escape(m.location) if m.location else ""
                if m.purpose:
                     details_flowables.append(Paragraph(escape(m.purpose), body_style_left))
        else:
            # No movement record implies generic defaults (On Duty, no location/remarks)
            pass

        data.append([
            str(row_index),
            Paragraph(depot_code, styles['BodyText']),
            Paragraph(supervisor_name, styles['BodyText']),
            Paragraph(designation, styles['BodyText']),
            Paragraph(status_text, styles['BodyText']),
            Paragraph(location_text, styles['BodyText']),
            details_flowables,
        ])
        
        if m and m.on_leave:
            style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), colors.lightpink))

    table = Table(data, colWidths=[35, 60, 120, 120, 60, 100, 250])
    table.setStyle(TableStyle(style_commands))
    table.repeatRows = 1
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

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

        # Use shared logic
        supervisors_with_movements = get_daily_movements_logic(target_date)

        serializer = SupervisorWithMovementSerializer(supervisors_with_movements, many=True)
        return Response(serializer.data)

class SupervisorMovementViewSet(viewsets.ModelViewSet):
    queryset = SupervisorMovement.objects.all()
    serializer_class = SupervisorMovementSerializer
    permission_classes = [permissions.AllowAny]

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

        # Use shared logic to include all supervisors and carry-over logic
        supervisors_with_movements = get_daily_movements_logic(target_date)

        pdf_buffer = generate_movement_report_pdf(target_date, supervisors_with_movements)
        pdf_filename = f"Movement_Report_{target_date.strftime('%Y-%m-%d')}.pdf"
        caption = f"Supervisor Movement Report for {target_date.strftime('%d-%b-%Y')}"

        # Send to Telegram groups: 'alerts' and 'reports'
        target_groups = ['alerts', 'reports']
        for group_key in target_groups:
            try:
                tg_group = TelegramGroup.objects.get(key=group_key)
                if tg_group.chat_id:
                    pdf_buffer.seek(0)
                    send_telegram_document(
                        chat_id=tg_group.chat_id,
                        document=pdf_buffer,
                        caption=caption,
                        filename=pdf_filename
                    )
            except Exception as e:
                # Log error but don't stop the download
                print(f"Failed to send report to Telegram group '{group_key}': {e}")
        
        pdf_buffer.seek(0)

        # Return file directly for download
        return FileResponse(
            pdf_buffer, 
            as_attachment=True, 
            filename=pdf_filename,
            content_type='application/pdf'
        )