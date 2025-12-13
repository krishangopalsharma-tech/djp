# Path: backend/failures/views.py
from rest_framework import viewsets, permissions, response, status, parsers
from rest_framework.decorators import action
from django.utils import timezone
from .models import Failure, FailureAttachment
from .serializers import FailureSerializer, FailureAttachmentSerializer
from .filters import FailureFilter # Added import

# --- START OF FIX: Add imports for Telegram ---
from telegram_notifications.bot import send_telegram_message, send_telegram_document, create_failure_keyboard
from telegram_notifications.models import TelegramGroup
from .utils import format_failure_message
# --- END OF FIX ---


class FailureViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Failure logs.
    """
    serializer_class = FailureSerializer
    permission_classes = [permissions.AllowAny]  # Use AllowAny for dev
    filterset_class = FailureFilter # Use the class
    search_fields = ['fail_id', 'circuit__name', 'station__name', 'remark_fail']

    def get_queryset(self):
        """
        Filter archived failures only for the list action.
        Detail actions (retrieve, update, archive, etc.) should access all failures.
        """
        if self.action == 'list':
            return Failure.objects.filter(is_archived=False).select_related(
                'circuit', 'station', 'section', 'sub_section', 'assigned_to'
            ).order_by('-reported_at')
        return Failure.objects.all().select_related(
            'circuit', 'station', 'section', 'sub_section', 'assigned_to'
        ).order_by('-reported_at')

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

    @action(detail=True, methods=['post'])
    def notify(self, request, pk=None):
        try:
            failure = self.get_object()
        except Failure.DoesNotExist:
            return response.Response({'error': 'Failure not found.'}, status=status.HTTP_404_NOT_FOUND)

        group_keys = request.data.get('groups', [])
        if not group_keys:
            group_keys = ['alerts']

        try:
            # 3. Build Message
            message = format_failure_message(failure)

            # 4. Send Logic
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

            # --- START OF FIX: Send to Supervisor ---
            if failure.assigned_to and failure.assigned_to.telegram_chat_id:
                try:
                    print(f"DEBUG: Sending to Supervisor {failure.assigned_to.name} ({failure.assigned_to.telegram_chat_id})")
                    keyboard = create_failure_keyboard(failure.fail_id)
                    print(f"DEBUG: Keyboard generated: {keyboard}")
                    send_telegram_message(
                        chat_id=failure.assigned_to.telegram_chat_id, 
                        text=message, 
                        reply_markup=keyboard
                    )
                    sent_to.append(f"Supervisor ({failure.assigned_to.name})")
                except Exception as e:
                    print(f"DEBUG: Error sending to supervisor: {e}")
                    failed_to.append(f"Supervisor ({str(e)})")
            else:
                print(f"DEBUG: No supervisor assigned or no chat ID. Assigned: {failure.assigned_to}")
            # --- END OF FIX ---

            if not sent_to:
                return response.Response({'error': f"Failed to send: {', '.join(failed_to)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            failure.was_notified = True
            failure.save(update_fields=['was_notified'])

            return response.Response({'message': f"Notification sent to: {', '.join(sent_to)}."})
        
        except Exception as e:
            return response.Response({'error': f'Failed to send message: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # --- END OF FIX ---


class FailureAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Failure Attachments.
    """
    queryset = FailureAttachment.objects.all()
    serializer_class = FailureAttachmentSerializer
    permission_classes = [permissions.AllowAny]  # Use AllowAny for dev
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filterset_fields = ['failure']

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        failure_id = request.data.get('failure')
        description = request.data.get('description', '')
        
        if not file_obj:
            return response.Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            failure = Failure.objects.get(pk=failure_id)
        except Failure.DoesNotExist:
            return response.Response({'error': 'Failure not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get Telegram Group
        try:
            group = TelegramGroup.objects.get(key='operations')
            if not group.chat_id:
                 return response.Response({'error': 'Operations group has no Chat ID.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except TelegramGroup.DoesNotExist:
             return response.Response({'error': 'Operations group not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Send to Telegram
        try:
            caption = f"<b>Attachment for Failure:</b> {failure.fail_id}\n<b>Description:</b> {description}"
            
            # Stream directly to Telegram
            telegram_msg = send_telegram_document(
                chat_id=group.chat_id,
                document=file_obj,
                caption=caption
            )
            
            # Save record
            attachment = FailureAttachment.objects.create(
                failure=failure,
                file=None, # No local file
                telegram_file_id=telegram_msg.document.file_id,
                telegram_message_id=telegram_msg.message_id,
                description=description,
                uploaded_by=request.user if request.user.is_authenticated else None
            )
            
            serializer = self.get_serializer(attachment)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return response.Response({'error': f'Failed to upload to Telegram: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)