# Path: backend/failures/views.py
from rest_framework import viewsets, permissions, response, status
from rest_framework.decorators import action
from django.utils import timezone
from .models import Failure, FailureAttachment
from .serializers import FailureSerializer, FailureAttachmentSerializer

# --- START OF FIX: Add imports for Telegram ---
from telegram_notifications.bot import send_telegram_message
from telegram_notifications.models import TelegramGroup
# --- END OF FIX ---


class FailureViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Failure logs.
    """
    queryset = Failure.objects.filter(is_archived=False).order_by('-reported_at')
    serializer_class = FailureSerializer
    permission_classes = [permissions.AllowAny]  # Use AllowAny for dev
    filterset_fields = ['current_status', 'severity', 'circuit', 'station', 'section', 'assigned_to']
    search_fields = ['fail_id', 'circuit__name', 'station__name', 'remark_fail']

    # This action is for the "ArchiveManagement.vue" component
    @action(detail=False, methods=['get'], url_path='archived')
    def list_archived(self, request):
        """
        Returns a list of all *archived* failures.
        """
        archived_failures = Failure.objects.filter(is_archived=True).order_by('-archived_at')
        page = self.paginate_queryset(archived_failures)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(archived_failures, many=True)
        return response.Response(serializer.data)

    # This action is for the "ArchiveManagement.vue" component
    @action(detail=True, methods=['delete'], url_path='permanent-delete')
    def permanent_delete(self, request, pk=None):
        """
        Permanently deletes a failure log.
        """
        try:
            failure = self.get_object()
            failure.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        except Failure.DoesNotExist:
            return response.Response({'error': 'Failure not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # This action is for the main Failure form
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archives a failure (sets is_archived=True).
        """
        try:
            failure = self.get_object()
            failure.is_archived = True
            failure.archived_at = timezone.now()
            failure.archived_reason = request.data.get('reason', '')
            failure.save()
            return response.Response(self.get_serializer(failure).data)
        except Failure.DoesNotExist:
            return response.Response({'error': 'Failure not found.'}, status=status.HTTP_404_NOT_FOUND)

    # --- START OF FIX: Add the missing 'notify' action ---
    @action(detail=True, methods=['post'])
    def notify(self, request, pk=None):
        """
        Sends a Telegram notification for a specific failure.
        """
        try:
            failure = self.get_object()
        except Failure.DoesNotExist:
            return response.Response({'error': 'Failure not found.'}, status=status.HTTP_404_NOT_FOUND)

        group_keys = request.data.get('groups', [])
        if not group_keys:
            return response.Response({'error': 'No notification groups provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Build the notification message
        try:
            message_lines = [
                "<b>🔔 Failure Notification 🔔</b>",
                f"<b>Event ID:</b> {failure.fail_id}",
            ]
            if failure.circuit:
                message_lines.append(f"<b>Circuit:</b> {failure.circuit.circuit_id} ({failure.circuit.name})")
            if failure.station:
                message_lines.append(f"<b>Station:</b> {failure.station.name}")
            if failure.section:
                message_lines.append(f"<b>Section:</b> {failure.section.name}")
            
            message_lines.append(f"<b>Reported:</b> {failure.reported_at.strftime('%d-%m-%Y %H:%M')}")
            message_lines.append(f"<b>Status:</b> {failure.current_status}")
            message_lines.append(f"<b>Severity:</b> {failure.severity}")
            
            if failure.remark_fail:
                message_lines.append(f"\n<b>Notes:</b> {failure.remark_fail}")
            
            message = "\n".join(message_lines)

            sent_to = []
            failed_to = []

            for key in group_keys:
                try:
                    group = TelegramGroup.objects.get(key=key)
                    if group.chat_id:
                        send_telegram_message(chat_id=group.chat_id, text=message)
                        sent_to.append(key)
                    else:
                        failed_to.append(f"{key} (no Chat ID)")
                except TelegramGroup.DoesNotExist:
                    failed_to.append(f"{key} (group not configured)")
                except Exception as e:
                    failed_to.append(f"{key} ({str(e)})")

            if not sent_to:
                return response.Response({'error': f"Failed to send to all groups: {', '.join(failed_to)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Mark the failure as notified
            failure.was_notified = True
            failure.save(update_fields=['was_notified'])

            return response.Response({'message': f"Notification sent to: {', '.join(sent_to)}."})
        
        except Exception as e:
            return response.Response({'error': f'Failed to build or send message: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # --- END OF FIX ---


class FailureAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Failure Attachments.
    """
    queryset = FailureAttachment.objects.all()
    serializer_class = FailureAttachmentSerializer
    permission_classes = [permissions.AllowAny]  # Use AllowAny for dev
    filterset_fields = ['failure']