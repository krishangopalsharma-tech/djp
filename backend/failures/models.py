from django.db import models, transaction
from django.utils import timezone
from core.models import TimestampedModel, FailureIDSettings
from infrastructure.models import Circuit, Station, Section, SubSection, Supervisor
import datetime

class Failure(TimestampedModel):
    ENTRY_TYPE_CHOICES = [
        ('item', 'Item'), ('message', 'Message'), ('warning', 'Warning'),
        ('major', 'Major'), ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'), ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'), ('On Hold', 'On Hold'),
    ]
    SEVERITY_CHOICES = [('Minor', 'Minor'), ('Major', 'Major'), ('Critical', 'Critical')]

    fail_id = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique Failure ID, auto-generated.")
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES, default='item')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='Minor')
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    circuit = models.ForeignKey(Circuit, on_delete=models.PROTECT, related_name="failures")
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True, related_name="failures")
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="failures")
    sub_section = models.ForeignKey(SubSection, on_delete=models.SET_NULL, null=True, blank=True, related_name="failures")
    assigned_to = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name="failures")
    reported_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    remark_fail = models.TextField(blank=True, help_text="Initial notes about the failure.")
    remark_right = models.TextField(blank=True, help_text="Notes on how the failure was resolved.")

    def __str__(self):
        return self.fail_id

    def save(self, *args, **kwargs):
        if not self.fail_id:
            # Use a database transaction to ensure data integrity
            with transaction.atomic():
                print("\n--- Attempting to generate new Failure ID ---")
                # Lock the settings row to prevent race conditions
                settings = FailureIDSettings.get_active_settings()
                print(f"1. Fetched Settings: Prefix='{settings.prefix}', Cycle='{settings.reset_cycle}', Last#='{settings.last_number}', LastReset='{settings.last_reset_date}'")

                now = timezone.now()
                new_number = settings.last_number
                
                # Check if the reset cycle needs to be triggered
                needs_reset = False
                if settings.reset_cycle == 'yearly' and now.year != settings.last_reset_date.year:
                    needs_reset = True
                    print("2. Condition met: Yearly reset")
                elif settings.reset_cycle == 'monthly' and (now.year != settings.last_reset_date.year or now.month != settings.last_reset_date.month):
                    needs_reset = True
                    print("2. Condition met: Monthly reset")
                else:
                    print("2. Condition not met for reset cycle.")

                if needs_reset:
                    new_number = 0
                    settings.last_reset_date = now.date()
                    print(f"3. Resetting counter. New number is 0. New reset date is {settings.last_reset_date}")
                
                new_number += 1
                settings.last_number = new_number
                settings.save()
                print(f"4. Incremented number. New last_number is {settings.last_number}. Saving settings.")

                # Format the ID string
                year_str = now.strftime('%Y')
                month_str = now.strftime('%m')
                padded_number = str(new_number).zfill(settings.padding_digits)
                
                if settings.reset_cycle == 'yearly':
                    self.fail_id = f"{settings.prefix}-{year_str}-{padded_number}"
                elif settings.reset_cycle == 'monthly':
                    self.fail_id = f"{settings.prefix}-{year_str}-{month_str}-{padded_number}"
                else: # 'never'
                    self.fail_id = f"{settings.prefix}-{padded_number}"
                
                print(f"5. Generated new Fail ID: {self.fail_id}")
                print("--- End of Failure ID Generation ---\n")

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-reported_at']

