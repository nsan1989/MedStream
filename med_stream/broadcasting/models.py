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
from media_library.models import MediaAsset


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
        DoctorSchedule,
        on_delete=models.CASCADE,
        related_name="broadcast_doctor",
        null=True,
        blank=True,
    )
    media = models.ForeignKey(
        MediaAsset,
        on_delete=models.CASCADE,
        related_name="broadcast_media",
        null=True,
        blank=True,
    )
    opdschedule = models.ForeignKey(
        OPDSchedule,
        on_delete=models.CASCADE,
        related_name="broadcast_opd",
        null=True,
        blank=True,
    )
    layout = models.ForeignKey(
        Layout,
        on_delete=models.SET_NULL,
        related_name="broadcast_layout",
        null=True,
        blank=True,
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

        # Skip schedule validation for
        # media / playlist broadcasts
        if not self.doctor_schedule_id and not self.opdschedule_id:
            return

        # Validate doctor/opd relationship only
        # if both are selected
        if self.doctor_schedule_id and self.opdschedule_id:
            if self.doctor_schedule.doctor_id != self.opdschedule.doctor_id:
                raise ValidationError(
                    {
                        "opdschedule": (
                            "Doctor schedule and OPD schedule "
                            "must belong to the same doctor."
                        )
                    }
                )

        doctor_org_id = None
        doctor_facility_id = None
        opd_org_id = None
        opd_facility_id = None

        if self.doctor_schedule_id:
            doctor_org_id = self.doctor_schedule.doctor.organization_id
            doctor_facility_id = self.doctor_schedule.doctor.facility_id

        if self.opdschedule_id:
            opd_org_id = self.opdschedule.doctor.organization_id
            opd_facility_id = self.opdschedule.opd_room.facility_id

        layout_org_id = self.layout.organization_id if self.layout_id else None

        broadcast_org_id = self.organization_id
        device_facility_id = self.device.facility_id
        broadcast_facility_id = self.facility_id

        # Organization validation
        known_orgs = {
            org_id
            for org_id in [
                doctor_org_id,
                opd_org_id,
            ]
            if org_id
        }

        if len(known_orgs) > 1:
            raise ValidationError(
                {
                    "organization": (
                        "Organization mismatch between "
                        "doctor schedule and OPD schedule."
                    )
                }
            )

        primary_org_id = next(iter(known_orgs)) if known_orgs else None

        if broadcast_org_id and primary_org_id and broadcast_org_id != primary_org_id:
            raise ValidationError(
                {
                    "organization": (
                        "Broadcast organization must " "match selected schedule."
                    )
                }
            )

        device_org_id = (
            self.device.facility.organization_id
            if self.device_id and self.device.facility_id
            else None
        )

        if device_org_id and primary_org_id and device_org_id != primary_org_id:
            raise ValidationError(
                {"device": ("Device organization must " "match schedule organization.")}
            )

        if layout_org_id and primary_org_id and layout_org_id != primary_org_id:
            raise ValidationError(
                {"layout": ("Layout organization must " "match schedule organization.")}
            )

        # Facility validation
        known_facilities = {
            f_id
            for f_id in [
                doctor_facility_id,
                opd_facility_id,
                device_facility_id,
            ]
            if f_id
        }

        if (
            broadcast_facility_id
            and len(known_facilities) > 0
            and broadcast_facility_id not in known_facilities
        ):
            raise ValidationError({"facility": ("Broadcast facility mismatch.")})

        if self.ended_at and self.started_at and self.ended_at <= self.started_at:
            raise ValidationError(
                {"ended_at": ("End time must be greater " "than start time.")}
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
