from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from supervisors.models import Supervisor
from .models import SupervisorMovement
from .serializers import SupervisorMovementSerializer, SupervisorWithMovementSerializer
from datetime import datetime
from telegram_notifications.models import TelegramGroup

import io
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4, landscape

def generate_movement_report_pdf(target_date, movements):
    """
    Generates a PDF report for supervisor movements and returns it as a file-like object.
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
    ]

    body_style = styles['BodyText']
    for i, m in enumerate(movements):
        row_index = i + 1
        
        status_text = "On Leave" if m.on_leave else "On Duty"
        depot_code = m.supervisor.depot.code if m.supervisor.depot and m.supervisor.depot.code else 'N/A'
        supervisor_name = m.supervisor.name
        designation = m.supervisor.designation
        
        location_text = ""
        details_flowables = []

        if m.on_leave:
            location_text = "N/A"
            date_range = "N/A"
            if m.leave_from and m.leave_to:
                date_range = f"{m.leave_from.strftime('%d-%b')} to {m.leave_to.strftime('%d-%b')}"
            details_flowables.append(Paragraph(f"Duration: {escape(date_range)}", body_style))
            if m.look_after:
                details_flowables.append(Paragraph(f"Looked After By: {escape(m.look_after.name)}", body_style))
        else:
            location_text = escape(m.location)
            if m.purpose:
                details_flowables.append(Paragraph(escape(m.purpose), body_style))

        data.append([
            str(row_index),
            Paragraph(depot_code, body_style),
            Paragraph(supervisor_name, body_style),
            Paragraph(designation, body_style),
            Paragraph(status_text, body_style),
            Paragraph(location_text, body_style),
            details_flowables,
        ])
        
        if m.on_leave:
            style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), colors.lightpink))

    table = Table(data, colWidths=[35, 60, 130, 130, 70, 70, 230])
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

        supervisors = Supervisor.objects.select_related('depot').all().order_by('name')
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