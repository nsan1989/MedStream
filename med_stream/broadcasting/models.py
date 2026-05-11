from django.db import models
from django.core.exceptions import ValidationError
import uuid
from core.models import TimeStampedModel
from schedules.models import OPDSchedule, DoctorSchedule
from devices.models import Device
from layouts.models import Layout
from .enums import BroadcastStatus


# Broadcast session model.
class BroadcastSession(TimeStampedModel):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broadcast_sessions",
    )
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="broadcast_sessions"
    )
    doctor_schedule = models.ForeignKey(
        DoctorSchedule, on_delete=models.CASCADE, related_name="broadcast_sessions"
    )
    opdschedule = models.ForeignKey(
        OPDSchedule, on_delete=models.CASCADE, related_name="broadcast_sessions"
    )
    layout = models.ForeignKey(
        Layout, on_delete=models.CASCADE, related_name="broadcast_sessions"
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=BroadcastStatus.choices,
        default=BroadcastStatus.SCHEDULED,
    )

    def clean(self):
        super().clean()

        if self.doctor_schedule.doctor_id != self.opdschedule.doctor_id:
            raise ValidationError(
                {
                    "opdschedule": (
                        "Doctor schedule and OPD schedule must belong to the same doctor."
                    )
                }
            )

        doctor_org_id = self.doctor_schedule.doctor.organization_id
        opd_org_id = self.opdschedule.doctor.organization_id
        layout_org_id = self.layout.organization_id
        broadcast_org_id = self.organization_id

        if doctor_org_id and opd_org_id and doctor_org_id != opd_org_id:
            raise ValidationError(
                {"doctor_schedule": "Doctor schedule and OPD schedule organization mismatch."}
            )

        if broadcast_org_id:
            if doctor_org_id and doctor_org_id != broadcast_org_id:
                raise ValidationError(
                    {"organization": "Broadcast organization must match doctor organization."}
                )
            if layout_org_id and layout_org_id != broadcast_org_id:
                raise ValidationError(
                    {"layout": "Layout must belong to the selected broadcast organization."}
                )

        if self.ended_at and self.ended_at <= self.started_at:
            raise ValidationError(
                {"ended_at": "End time must be greater than start time."}
            )

    def __str__(self):
        return f"BroadcastSession {self.id} on Device {self.device.name}"
