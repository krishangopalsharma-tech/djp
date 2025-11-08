from django.db import models
from core.models import TimestampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from telegram_notifications.models import TelegramGroup
from telegram_notifications.bot import send_telegram_document
from xml.sax.saxutils import escape

def attachment_upload_path(instance, filename):
    return f'attachments/failures/{instance.failure.fail_id}/{filename}'

class Failure(TimestampedModel):
    fail_id = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique Failure ID, auto-generated.")
    entry_type = models.CharField(max_length=10, choices=[('item', 'Item'), ('message', 'Message'), ('warning', 'Warning'), ('major', 'Major'), ('critical', 'Critical')], default='item')
    severity = models.CharField(max_length=10, choices=[('Minor', 'Minor'), ('Major', 'Major'), ('Critical', 'Critical')], default='Minor')
    current_status = models.CharField(max_length=20, choices=[('Draft', 'Draft'), ('Active', 'Active'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved'), ('On Hold', 'On Hold'), ('Information', 'Information')], default='Active')
    reported_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    remark_fail = models.TextField(blank=True, help_text="Initial notes about the failure.")
    remark_right = models.TextField(blank=True, help_text="Notes on how the failure was resolved.")
    was_notified = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_reason = models.TextField(blank=True)
    # Foreign Keys
    circuit = models.ForeignKey('circuits.Circuit', on_delete=models.CASCADE, null=True, blank=True)
    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey('sections.Section', on_delete=models.CASCADE, null=True, blank=True)
    sub_section = models.ForeignKey('sections.SubSection', on_delete=models.CASCADE, null=True, blank=True)
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)


class FailureAttachment(TimestampedModel):
    failure = models.ForeignKey(Failure, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=attachment_upload_path)
    description = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

@receiver(post_save, sender=FailureAttachment)
def on_attachment_saved(sender, instance, created, **kwargs):
    if created:
        try:
            # Send to 'alerts' group by default
            group = TelegramGroup.objects.get(key='alerts')
            if group.chat_id:
                failure = instance.failure
                caption_lines = [
                    f"<b>📎 Attachment Added to Event {escape(failure.fail_id)}</b>",
                    f"<b>Circuit:</b> {escape(failure.circuit.circuit_id if failure.circuit else 'N/A')}",
                    f"<b>Station:</b> {escape(failure.station.name if failure.station else 'N/A')}",
                ]
                if instance.description:
                    caption_lines.append(f"\n<b>Description:</b> {escape(instance.description)}")

                caption = "\n".join(caption_lines)

                # Open the file in binary read mode
                with instance.file.open('rb') as f:
                    send_telegram_document(
                        chat_id=group.chat_id,
                        document=f,
                        caption=caption
                    )
        except TelegramGroup.DoesNotExist:
            print(f"Telegram group 'alerts' not found. Cannot send attachment notification.")
        except Exception as e:
            print(f"Error sending attachment to Telegram: {e}")
