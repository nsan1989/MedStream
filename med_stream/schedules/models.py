import uuid
from django.db import models
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel
from organizations.models import Organization
from facilities.models import Facility, Block, Floor
from django.utils import timezone


# Department model.
class Department(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=255)

    def clean(self):
        super().clean()

        dept_qs = Department.objects.filter(name__iexact=self.name)
        if self.pk:
            dept_qs = dept_qs.exclude(pk=self.pk)
        if dept_qs.exists():
            raise ValidationError(
                {"name": "A department with this name already exists."}
            )

    def __str__(self):
        return self.name


# Doctor model.
class Doctor(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    facility = models.ForeignKey(Facility, models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True
    )
    qualification = models.CharField(max_length=255, blank=True)
    experience = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        super().clean()

        doctor_qs = Doctor.objects.filter(
            name=self.name, organization=self.organization, facility=self.facility
        )
        if self.pk:
            doctor_qs = doctor_qs.exclude(pk=self.pk)
        if doctor_qs.exists():
            raise ValidationError(
                {"user": "This doctor profile already exists for the organization."}
            )

    def __str__(self):
        name = (self.name or "").strip()
        dept_name = self.department.name if self.department else ""

        if name and dept_name:
            return f"{name} - {dept_name}"
        if name:
            return name
        if dept_name:
            return dept_name
        return f"Doctor {self.pk}"


# OPD Room model.
class OPDRoom(TimeStampedModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opd_rooms",
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opd_rooms",
    )
    block = models.ForeignKey(
        Block,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opd_rooms",
    )
    floor = models.ForeignKey(
        Floor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opd_rooms",
    )
    is_active = models.BooleanField(default=True)

    def clean(self):
        super().clean()

        if self.organization and self.facility:
            if self.facility.organization_id != self.organization_id:
                raise ValidationError(
                    {"facility": "Facility must belong to the selected organization."}
                )

        if self.block and self.facility:
            if self.block.facility_id != self.facility_id:
                raise ValidationError(
                    {"block": "Block must belong to the selected facility."}
                )

        if self.floor and self.block:
            if self.floor.block_id != self.block_id:
                raise ValidationError(
                    {"floor": "Floor must belong to the selected block."}
                )

        if self.floor and self.facility and self.floor.block:
            if self.floor.block.facility_id != self.facility_id:
                raise ValidationError(
                    {"floor": "Floor must belong to the selected facility."}
                )

        room_qs = OPDRoom.objects.filter(
            name__iexact=self.name, organization=self.organization
        )
        if self.pk:
            room_qs = room_qs.exclude(pk=self.pk)
        if room_qs.exists():
            raise ValidationError(
                {
                    "name": "An OPD Room with this name already exists for the organization."
                }
            )

    def __str__(self):
        details = []
        if self.block:
            details.append(str(self.block))
        if self.floor:
            details.append(str(self.floor))

        if details:
            return f"{self.name} ({' / '.join(details)})"

        return self.name


# Doctor schedule model.
class DoctorSchedule(TimeStampedModel):
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="doctor_schedules"
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True, null=True)

    def clean(self):
        super().clean()

        if self.start_date > self.end_date:
            raise ValidationError(
                {
                    "end_date": "Out of station end date must be on or after the start date."
                }
            )

        overlapping_qs = DoctorSchedule.objects.filter(
            doctor=self.doctor,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        )

        if self.pk:
            overlapping_qs = overlapping_qs.exclude(pk=self.pk)

        if overlapping_qs.exists():
            raise ValidationError(
                {
                    "start_date": (
                        "This out-of-station period overlaps with an existing record."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.doctor} out of station "
            f"from {self.start_date} to {self.end_date}"
        )


# OPD Schedule model.
class OPDSchedule(TimeStampedModel):
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="opd_schedules"
    )
    opd_date = models.DateField(null=True, blank=True)
    opd_room = models.ForeignKey(
        OPDRoom, on_delete=models.CASCADE, related_name="opd_schedules"
    )

    day_of_week = models.IntegerField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ],
        null=True,
        blank=True,
    )

    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def clean(self):
        super().clean()

        doctor = self.doctor if self.doctor_id else None
        opd_room = self.opd_room if self.opd_room_id else None

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time."})

        if doctor and opd_room:
            doctor_org_id = doctor.organization_id
            room_org_id = opd_room.organization_id

            if doctor_org_id and room_org_id and doctor_org_id != room_org_id:
                raise ValidationError(
                    {
                        "opd_room": (
                            "Doctor and OPD room must belong "
                            "to the same organization."
                        )
                    }
                )

        if self.opd_date and self.day_of_week is not None:
            if self.opd_date.weekday() != self.day_of_week:
                raise ValidationError(
                    {
                        "day_of_week": "Day of week must match the selected OPD date."
                    }
                )

        today = timezone.localdate()
        target_date = self.opd_date
        if doctor and not target_date and self.day_of_week == today.weekday():
            target_date = today

        if doctor and target_date:
            is_out_of_station = DoctorSchedule.objects.filter(
                doctor=doctor,
                start_date__lte=target_date,
                end_date__gte=target_date,
            ).exists()

            if is_out_of_station:
                raise ValidationError(
                    {"doctor": ("Doctor is currently out of station.")}
                )

        if all([doctor, opd_room, self.start_time, self.end_time]):
            if self.opd_date:
                schedule_qs = OPDSchedule.objects.filter(
                    doctor=doctor,
                    opd_date=self.opd_date,
                )
            elif self.day_of_week is not None:
                schedule_qs = OPDSchedule.objects.filter(
                    doctor=doctor,
                    day_of_week=self.day_of_week,
                )
            else:
                schedule_qs = OPDSchedule.objects.none()

            if self.pk:
                schedule_qs = schedule_qs.exclude(pk=self.pk)

            for schedule in schedule_qs:
                if (
                    self.start_time < schedule.end_time
                    and self.end_time > schedule.start_time
                ):
                    raise ValidationError(
                        {
                            "start_time": (
                                "This schedule overlaps with an existing schedule."
                            )
                        }
                    )

    def save(self, *args, **kwargs):
        if self.opd_date:
            self.day_of_week = self.opd_date.weekday()
        super().save(*args, **kwargs)

    def __str__(self):
        doctor_name = getattr(self.doctor, "name", "Unknown")
        room_name = getattr(self.opd_room, "name", "Room")
        date_text = (
            self.opd_date.strftime("%d %b %Y")
            if self.opd_date
            else self.get_day_of_week_display()
        )

        return (
            f"{doctor_name} - {room_name} "
            f"{date_text} "
            f"from {self.start_time} to {self.end_time}"
        )
