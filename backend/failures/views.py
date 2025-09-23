# Path: backend/failures/views.py

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
    # select_related is a performance optimization. It fetches the related
    # objects in a single database query, preventing many extra queries.
    queryset = Failure.objects.filter(is_archived=False).select_related(
        'circuit', 'station', 'section', 'sub_section', 'assigned_to'
    ).all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        """
        Choose which serializer to use based on the action.
        - Use FailureCreateUpdateSerializer for creating and updating.
        - Use FailureListSerializer for listing and retrieving.
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

    # In a future step, we will add logic here to auto-generate the `fail_id`.

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

        message = (
            f"Failure ID: {failure.fail_id}\n"
            f"Circuit: {failure.circuit.name if failure.circuit else 'N/A'}\n"
            f"Status: {failure.current_status}\n"
            f"Remarks: {failure.remark_fail}"
        )

        groups = TelegramGroup.objects.filter(key__in=group_keys)
        chat_ids = [group.chat_id for group in groups if group.chat_id]

        if not chat_ids:
            return Response(
                {"error": "No valid chat_ids found for the provided groups."},
                status=status.HTTP_400_BAD_REQUEST
            )

        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not bot_token:
            return Response(
                {"error": "Telegram bot token is not configured."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        errors = []

        for chat_id in chat_ids:
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                errors.append(f"Failed to send to {chat_id}: {str(e)}")

        if errors:
            return Response(
                {"error": "Some notifications failed to send.", "details": errors},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"message": "Notifications sent successfully."})


class FailureAttachmentViewSet(viewsets.ModelViewSet):
    queryset = FailureAttachment.objects.all()
    serializer_class = FailureAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['failure']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
