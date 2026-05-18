from django.db import models
from django.core.exceptions import ValidationError
import uuid
from core.models import TimeStampedModel
from schedules.models import OPDSchedule, DoctorSchedule
from devices.models import Device
from layouts.models import Layout
from .enums import BroadcastStatus
from organizations.models import Organization
from facilities.models import Facility


# Broadcast session model.
class BroadcastSession(TimeStampedModel):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broadcast_organizations",
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broadcast_facility",
    )
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="broadcast_device"
    )
    doctor_schedule = models.ForeignKey(
        DoctorSchedule, on_delete=models.CASCADE, related_name="broadcast_doctor"
    )
    opdschedule = models.ForeignKey(
        OPDSchedule, on_delete=models.CASCADE, related_name="broadcast_opd"
    )
    layout = models.ForeignKey(
        Layout, on_delete=models.CASCADE, related_name="broadcast_layout"
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

        if not self.doctor_schedule_id or not self.opdschedule_id:
            return

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
        device_facility_id = self.device.facility_id
        doctor_facility_id = self.doctor_schedule.doctor.facility_id
        opd_facility_id = self.opdschedule.opd_room.facility_id
        broadcast_facility_id = self.facility_id

        if doctor_org_id and opd_org_id and doctor_org_id != opd_org_id:
            raise ValidationError(
                {
                    "doctor_schedule": "Doctor schedule and OPD schedule organization mismatch."
                }
            )

        if broadcast_org_id:
            if doctor_org_id and doctor_org_id != broadcast_org_id:
                raise ValidationError(
                    {
                        "organization": "Broadcast organization must match doctor organization."
                    }
                )
            if layout_org_id and layout_org_id != broadcast_org_id:
                raise ValidationError(
                    {
                        "layout": "Layout must belong to the selected broadcast organization."
                    }
                )
        if (
            self.device.organization_id
            and doctor_org_id
            and self.device.organization_id != doctor_org_id
        ):
            raise ValidationError(
                {"device": "Device organization must match doctor organization."}
            )

        if (
            self.layout.organization_id
            and doctor_org_id
            and self.layout.organization_id != doctor_org_id
        ):
            raise ValidationError(
                {"layout": "Layout organization must match doctor organization."}
            )

        if broadcast_facility_id:
            if doctor_facility_id and doctor_facility_id != broadcast_facility_id:
                raise ValidationError(
                    {
                        "facility": "Broadcast facility must match doctor facility."
                    }
                )
            if device_facility_id and device_facility_id != broadcast_facility_id:
                raise ValidationError(
                    {
                        "device": "Device facility must match selected broadcast facility."
                    }
                )
            if opd_facility_id and opd_facility_id != broadcast_facility_id:
                raise ValidationError(
                    {"opdschedule": "OPD room facility must match broadcast facility."}
                )
        else:
            known_facilities = {
                f_id
                for f_id in [doctor_facility_id, device_facility_id, opd_facility_id]
                if f_id
            }
            if len(known_facilities) > 1:
                raise ValidationError(
                    {
                        "facility": (
                            "Facility mismatch across doctor, OPD room, and device. "
                            "Select a facility explicitly."
                        )
                    }
                )

        if self.started_at:
            started_weekday = self.started_at.weekday()
            started_time = self.started_at.time()

            if started_weekday != self.doctor_schedule.day_of_week:
                raise ValidationError(
                    {
                        "started_at": (
                            "Start datetime day does not match doctor schedule day."
                        )
                    }
                )
            if started_weekday != self.opdschedule.day_of_week:
                raise ValidationError(
                    {
                        "started_at": "Start datetime day does not match OPD schedule day."
                    }
                )

            if not (
                self.doctor_schedule.start_time
                <= started_time
                < self.doctor_schedule.end_time
            ):
                raise ValidationError(
                    {
                        "started_at": (
                            "Start time must be within the selected doctor schedule window."
                        )
                    }
                )
            if not (self.opdschedule.start_time <= started_time < self.opdschedule.end_time):
                raise ValidationError(
                    {
                        "started_at": (
                            "Start time must be within the selected OPD schedule window."
                        )
                    }
                )

        if self.ended_at and self.ended_at <= self.started_at:
            raise ValidationError(
                {"ended_at": "End time must be greater than start time."}
            )

    def save(self, *args, **kwargs):
        if self.doctor_schedule_id:
            doctor = self.doctor_schedule.doctor
            if not self.organization_id:
                self.organization = doctor.organization
            if not self.facility_id:
                self.facility = doctor.facility

        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"BroadcastSession {self.id} on Device {self.device.name}"
