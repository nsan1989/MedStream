import uuid
from django.db import models
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel
from organizations.models import Organization
from facilities.models import Facility, Block, Floor


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


# OPD Schedule model.
class OPDSchedule(TimeStampedModel):
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="opd_schedules"
    )
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
        ]
    )

    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def clean(self):
        super().clean()

        # Prevent None comparison
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(
                    {"end_time": "End time must be after start time."}
                )

        # Prevent doctor/opd_room None error
        if self.doctor and self.opd_room:
            doctor_org_id = self.doctor.organization_id
            room_org_id = self.opd_room.organization_id

            if doctor_org_id and room_org_id and doctor_org_id != room_org_id:
                raise ValidationError(
                    {
                        "opd_room": (
                            "Doctor and OPD room must belong "
                            "to the same organization."
                        )
                    }
                )

        # Run overlap validation only if required fields exist
        if all(
            [
                self.doctor,
                self.opd_room,
                self.day_of_week is not None,
                self.start_time,
                self.end_time,
            ]
        ):
            schedule_qs = OPDSchedule.objects.filter(
                doctor=self.doctor,
                opd_room=self.opd_room,
                day_of_week=self.day_of_week,
            )

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
                                "This schedule overlaps with an " "existing schedule."
                            )
                        }
                    )

    def __str__(self):
        return (
            f"{self.doctor} - {self.opd_room} "
            f"on {self.get_day_of_week_display()} "
            f"from {self.start_time} to {self.end_time}"
        )


# Doctor schedule model.
class DoctorSchedule(TimeStampedModel):
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="doctor_schedules"
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
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def clean(self):
        super().clean()

        if self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time."})

        schedule_qs = DoctorSchedule.objects.filter(
            doctor=self.doctor, day_of_week=self.day_of_week
        )
        if self.pk:
            schedule_qs = schedule_qs.exclude(pk=self.pk)
        for schedule in schedule_qs:
            if (
                self.start_time < schedule.end_time
                and self.end_time > schedule.start_time
            ):
                raise ValidationError(
                    {
                        "start_time": "This schedule overlaps with an existing schedule for the doctor."
                    }
                )

    def __str__(self):
        return f"{self.doctor} on {self.get_day_of_week_display()} from {self.start_time} to {self.end_time}"
