import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from notifications.models import TelegramGroup
from .models import Failure, FailureAttachment
from .serializers import FailureListSerializer, FailureCreateUpdateSerializer, FailureAttachmentSerializer

class FailureViewSet(viewsets.ModelViewSet):
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
        """
        Custom action to send a Telegram notification for a failure.
        """
        failure = self.get_object()
        group_keys = request.data.get('groups', [])

        if not group_keys:
            return Response(
                {"error": "No notification groups provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Status Formatting Logic
        status_text = failure.current_status
        if status_text == 'Active':
            status_formatted = f"{status_text} 🔴"
        elif status_text == 'Resolved':
            status_formatted = f"{status_text} ✅"
        elif status_text == 'In Progress':
            status_formatted = f"{status_text} 🟡"
        elif status_text == 'On Hold':
            status_formatted = f"{status_text} 🟠"
        else:
            status_formatted = status_text

        # Message format with bold labels
        message_parts = [f"*ID*: {failure.fail_id}\n"]
        message_parts.append(f"*Circuit*: {failure.circuit.name if failure.circuit else 'N/A'}")
        message_parts.append(f"*Status*: {status_formatted}\n")

        if failure.station:
            message_parts.append(f"*Station*: {failure.station.name}")
        if failure.section:
            message_parts.append(f"*Section*: {failure.section.name}")
        if failure.sub_section:
            message_parts.append(f"*Sub Section*: {failure.sub_section.name}")
        if failure.assigned_to:
            message_parts.append(f"*Assigned To*: {failure.assigned_to.name}")
        
        if any([failure.station, failure.section, failure.sub_section, failure.assigned_to]):
            message_parts.append("")

        if failure.remark_fail:
            message_parts.append(f"*Remarks*: {failure.remark_fail}\n")

        tag_parts = []
        if failure.circuit: tag_parts.append(f"#{failure.circuit.name.replace(' ', '_')}")
        if failure.station: tag_parts.append(f"#{failure.station.name.replace(' ', '_')}")
        if failure.section: tag_parts.append(f"#{failure.section.name.replace(' ', '_')}")
        if tag_parts:
            message_parts.append("*Tags*: " + " ".join(tag_parts))

        message = "\n".join(message_parts)
        
        try:
            groups_to_notify = TelegramGroup.objects.filter(key__in=group_keys)
            if not groups_to_notify.exists():
                return Response(
                    {"error": "No valid Telegram groups found for the provided keys."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for group in groups_to_notify:
                group.send_message(message)

            return Response({"message": "Notifications sent successfully."})
        
        except Exception as e:
            return Response(
                {"error": f"Failed to send notification: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FailureAttachmentViewSet(viewsets.ModelViewSet):
    queryset = FailureAttachment.objects.all()
    serializer_class = FailureAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['failure']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)