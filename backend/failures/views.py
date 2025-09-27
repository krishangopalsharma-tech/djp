import requests
import re # Make sure 're' is imported
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import html # <-- ADD THIS IMPORT
from rest_framework.views import APIView

from notifications.models import TelegramGroup
from .models import Failure, FailureAttachment
from .serializers import FailureListSerializer, FailureCreateUpdateSerializer, FailureAttachmentSerializer

class FailureViewSet(viewsets.ModelViewSet):
    # ... (other methods are unchanged) ...
    """
    API endpoint that allows failures to be viewed or edited.
    """
    # Optimized queryset to prevent N+1 query issues
    queryset = Failure.objects.filter(is_archived=False).select_related(
        'circuit', 'station', 'section', 'sub_section', 'assigned_to'
    ).all()
    
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        """
        Choose which serializer to use based on the action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return FailureCreateUpdateSerializer
        return FailureListSerializer

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Custom action to archive a failure log instead of deleting it.
        """
        failure = self.get_object()
        failure.is_archived = True
        failure.archived_at = timezone.now()
        failure.archived_reason = request.data.get('reason', '')
        failure.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def notify(self, request, pk=None):
        failure = self.get_object()
        group_keys = request.data.get('groups', [])
        if not group_keys:
            return Response({"error": "No notification groups provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Status Formatting Logic with emojis
        status_text = failure.current_status
        status_emoji = ''
        if status_text == 'Active': status_emoji = ' 🔴'
        elif status_text == 'Resolved': status_emoji = ' ✅'
        elif status_text == 'In Progress': status_emoji = ' 🟡'
        elif status_text == 'On Hold': status_emoji = ' 🟠'
        elif status_text == 'Information': status_emoji = ' ℹ️'

        # Build the message using Markdown syntax
        message_parts = [f"*ID:* {failure.fail_id}"]
        message_parts.append("") # Add a blank line
        message_parts.append(f"*Circuit:* {failure.circuit.circuit_id if failure.circuit else 'N/A'}")
        message_parts.append(f"*Status:* {status_text}{status_emoji}")
        message_parts.append("") # Add a blank line
        
        station_display = (failure.station.code or failure.station.name) if failure.station else 'N/A'
        section_display = failure.section.name if failure.section else 'N/A'

        if failure.entry_type == 'item' or (station_display not in ['ALL', 'N/A']):
            message_parts.append(f"*Station:* {station_display}")
        if failure.entry_type == 'item' or (section_display not in ['ALL', 'N/A']):
            message_parts.append(f"*Section:* {section_display}")
        
        message_parts.append("") # Add a blank line

        if failure.remark_fail:
            truncated_remarks = (failure.remark_fail[:1000] + '...') if len(failure.remark_fail) > 1000 else failure.remark_fail
            message_parts.append(f"*Remarks:*\n{truncated_remarks}")

        # Build tag string
        tag_parts = []
        def sanitize_for_tag(text):
            return re.sub(r'[^a-zA-Z0-9_]', '', str(text).replace(' ', '_')) if text else ''
        if failure.entry_type == 'message':
            tag_parts.append("#GeneralMessage")
        else:
            if failure.circuit and failure.circuit.name != 'Info':
                safe_tag = sanitize_for_tag(failure.circuit.circuit_id)
                if safe_tag: tag_parts.append(f"#{safe_tag}")
            if failure.station and failure.station.name != 'ALL':
                safe_tag = sanitize_for_tag(failure.station.code or failure.station.name)
                if safe_tag: tag_parts.append(f"#{safe_tag}")
            if failure.section and failure.section.name != 'ALL':
                safe_tag = sanitize_for_tag(failure.section.name)
                if safe_tag: tag_parts.append(f"#{safe_tag}")
        
        if tag_parts:
            message_parts.append("") # Add a blank line before tags
            message_parts.append("*Tags:* " + " ".join(tag_parts))

        # Join parts with newlines for Markdown
        message = "\n".join(message_parts)
        
        frontend_url = f"{settings.FRONTEND_BASE_URL}/failures/edit/{failure.id}"
        
        inline_keyboard = [
            [
                {"text": "➡️ In Progress", "callback_data": f"update_status:{failure.id}:In Progress"},
                {"text": "✅ Resolve", "callback_data": f"update_status:{failure.id}:Resolved"},
                {"text": "📎 Upload File", "url": frontend_url}
            ]
        ]
        
        try:
            groups_to_notify = TelegramGroup.objects.filter(key__in=group_keys)
            for group in groups_to_notify:
                group.send_message(message, inline_keyboard=inline_keyboard)
            return Response({"message": "Notifications sent successfully."})
        except Exception as e:
            return Response({"error": f"Failed to send notification: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FailureAttachmentTelegramView(APIView):
    """
    Accepts a file upload and sends it directly to a designated Telegram group.
    """
    permission_classes = [permissions.AllowAny] # Adjust in production
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        failure_id = request.data.get('failure_id')
        uploaded_file = request.data.get('file')
        description = request.data.get('description', '')

        if not failure_id or not uploaded_file:
            return Response(
                {"error": "A failure_id and a file are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            failure = Failure.objects.select_related('circuit', 'station', 'section').get(id=failure_id)
            tg_group = TelegramGroup.objects.get(key='files')
        except Failure.DoesNotExist:
            return Response({"error": "Failure not found."}, status=status.HTTP_404_NOT_FOUND)
        except TelegramGroup.DoesNotExist:
            return Response({"error": "The 'files' Telegram group is not configured in the admin panel."}, status=status.HTTP_400_BAD_REQUEST)

        # --- SAFER DATA ACCESS ---
        circuit_id_str = failure.circuit.circuit_id if failure.circuit else 'N/A'
        station_display_str = failure.station.code if failure.station and failure.station.code else (failure.station.name if failure.station else 'N/A')

        # Calculate duration
        duration_str = 'N/A'
        if failure.reported_at and failure.resolved_at:
            duration_delta = failure.resolved_at - failure.reported_at
            hours, remainder = divmod(duration_delta.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = f"{int(hours)}h {int(minutes)}m"

        # Sanitize text for hashtags
        def sanitize_for_tag(text):
            return re.sub(r'[^a-zA-Z0-9_]', '', str(text).replace(' ', '_')) if text else ''

        # Build caption
        caption_parts = [
            f"<b>File Uploaded for Failure ID:</b> {html.escape(failure.fail_id)}",
            f"<b>Circuit:</b> {html.escape(circuit_id_str)}",
            f"<b>Station:</b> {html.escape(station_display_str)}",
            f"<b>Description:</b> {html.escape(description)}" if description else None,
            f"<b>Resolution Remarks:</b> {html.escape(failure.remark_right)}" if failure.remark_right else None,
            f"<b>Duration:</b> {duration_str}",
            "---",
            f"#{sanitize_for_tag(circuit_id_str)} #{sanitize_for_tag(station_display_str)}"
        ]
        
        caption = "\n".join(filter(None, caption_parts))

        try:
            uploaded_file.seek(0)
            tg_group.send_document(
                file_object=uploaded_file,
                filename=uploaded_file.name,
                caption=caption
            )
            return Response({"message": "File sent to Telegram successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            # This will now print the detailed Telegram error to your console
            print(f"TELEGRAM API ERROR: {e}") 
            return Response({"error": f"Failed to send document to Telegram: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class FailureAttachmentViewSet(viewsets.ModelViewSet):
    queryset = FailureAttachment.objects.all()
    serializer_class = FailureAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['failure']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
