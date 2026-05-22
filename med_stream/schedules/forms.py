from django import forms
from .models import Department, Doctor, OPDRoom, OPDSchedule, DoctorSchedule
from facilities.models import Facility, Block, Floor


# Add department form.
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        department = super().save(commit=False)

        if self.user and self.user.organization:
            department.organization = self.user.organization

        if commit:
            department.save()

        return department


# Add doctor form.
class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "name",
            "facility",
            "department",
            "qualification",
            "experience",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.organization:
            self.fields["facility"].queryset = Facility.objects.filter(
                organization=self.user.organization, is_active=True
            )

            self.fields["department"].queryset = Department.objects.none()

    def save(self, commit=True):
        doctor = super().save(commit=False)

        doctor.organization = self.user.organization

        if commit:
            doctor.save()

        return doctor


# Add OPD room form.
class OPDRoomForm(forms.ModelForm):
    class Meta:
        model = OPDRoom
        fields = [
            "facility",
            "block",
            "floor",
            "name",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["facility"].queryset = Facility.objects.none()
        self.fields["block"].queryset = Block.objects.none()
        self.fields["floor"].queryset = Floor.objects.none()

        if self.user and self.user.organization:
            self.fields["facility"].queryset = Facility.objects.filter(
                organization=self.user.organization,
                is_active=True,
            ).order_by("name")

        facility_id = self.data.get("facility") or getattr(
            self.instance, "facility_id", None
        )
        block_id = self.data.get("block") or getattr(self.instance, "block_id", None)

        if facility_id and self.user and self.user.organization:
            self.fields["block"].queryset = Block.objects.filter(
                facility_id=facility_id,
                facility__organization=self.user.organization,
                facility__is_active=True,
            ).order_by("name")

        if block_id and self.user and self.user.organization:
            self.fields["floor"].queryset = Floor.objects.filter(
                block_id=block_id,
                block__facility__organization=self.user.organization,
                block__facility__is_active=True,
            ).order_by("name")

    def save(self, commit=True):
        opd_room = super().save(commit=False)

        if self.user and self.user.organization:
            opd_room.organization = self.user.organization

        if commit:
            opd_room.save()

        return opd_room


# Add OPD schedule form.
class OPDScheduleForm(forms.ModelForm):
    day_of_week = forms.MultipleChoiceField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ],
        widget=forms.CheckboxSelectMultiple,
        label="Day of week",
    )

    class Meta:
        model = OPDSchedule
        fields = [
            "doctor",
            "opd_room",
            "start_time",
            "end_time",
            "is_available",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["doctor"].queryset = Doctor.objects.none()
        self.fields["opd_room"].queryset = OPDRoom.objects.none()

        if self.instance and self.instance.pk:
            self.fields["day_of_week"].initial = [self.instance.day_of_week]

        if self.user and self.user.organization:
            self.fields["doctor"].queryset = Doctor.objects.filter(
                organization=self.user.organization,
                is_active=True,
            )
            room_qs = OPDRoom.objects.filter(
                organization=self.user.organization,
                is_active=True,
            )
            if getattr(self.user, "facility", None):
                room_qs = room_qs.filter(facility=self.user.facility)
            self.fields["opd_room"].queryset = room_qs

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        opd_room = cleaned_data.get("opd_room")

        if not self.user or not getattr(self.user, "organization", None):
            return cleaned_data

        user_org = self.user.organization

        if doctor and doctor.organization_id != user_org.id:
            self.add_error("doctor", "Selected doctor is outside your organization.")

        if opd_room and opd_room.organization_id != user_org.id:
            self.add_error(
                "opd_room", "Selected OPD room is outside your organization."
            )

        if (
            opd_room
            and getattr(self.user, "facility", None)
            and opd_room.facility_id
            and opd_room.facility_id != self.user.facility_id
        ):
            self.add_error("opd_room", "Selected OPD room is outside your facility.")

        day_values = cleaned_data.get("day_of_week")
        if day_values:
            selected_days = [int(day) for day in day_values]
            start_time = cleaned_data.get("start_time")
            end_time = cleaned_data.get("end_time")

            if self.instance.pk and len(selected_days) > 1:
                self.add_error(
                    "day_of_week",
                    "You cannot select more than one day when editing an existing schedule.",
                )
            elif doctor and opd_room and start_time and end_time:
                for day in selected_days:
                    schedule_qs = OPDSchedule.objects.filter(
                        doctor=doctor,
                        opd_room=opd_room,
                        day_of_week=day,
                    )
                    if self.instance.pk:
                        schedule_qs = schedule_qs.exclude(pk=self.instance.pk)

                    for schedule in schedule_qs:
                        if (
                            start_time < schedule.end_time
                            and end_time > schedule.start_time
                        ):
                            self.add_error(
                                "day_of_week",
                                "This schedule overlaps with an existing schedule for the selected day(s).",
                            )
                            break

        return cleaned_data

    def save(self, commit=True):
        if self.instance.pk:
            day_values = self.cleaned_data.get("day_of_week")
            if day_values:
                self.instance.day_of_week = int(day_values[0])
            return super().save(commit=commit)

        created_schedules = []
        for day in [int(day) for day in self.cleaned_data.get("day_of_week", [])]:
            schedule = self.Meta.model(
                doctor=self.cleaned_data["doctor"],
                opd_room=self.cleaned_data["opd_room"],
                day_of_week=day,
                start_time=self.cleaned_data["start_time"],
                end_time=self.cleaned_data["end_time"],
                is_available=self.cleaned_data["is_available"],
            )
            if commit:
                schedule.save()
            created_schedules.append(schedule)

        return created_schedules


# Doctor schedule.
class DoctorScheduleForm(forms.ModelForm):
    day_of_week = forms.MultipleChoiceField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ],
        widget=forms.CheckboxSelectMultiple,
        label="Day of week",
        required=False,
    )

    class Meta:
        model = DoctorSchedule
        fields = [
            "doctor",
            "start_time",
            "end_time",
            "out_of_station_start_date",
            "out_of_station_end_date",
            "is_available",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "out_of_station_start_date": forms.DateInput(attrs={"type": "date"}),
            "out_of_station_end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["doctor"].queryset = Doctor.objects.none()

        if self.instance and self.instance.pk:
            self.fields["day_of_week"].initial = [self.instance.day_of_week]

        if self.user and self.user.organization:
            doctor_qs = Doctor.objects.filter(
                organization=self.user.organization,
                is_active=True,
            )
            if getattr(self.user, "facility", None):
                doctor_qs = doctor_qs.filter(facility=self.user.facility)
            self.fields["doctor"].queryset = doctor_qs

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        day_values = cleaned_data.get("day_of_week")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if not self.user or not getattr(self.user, "organization", None):
            return cleaned_data

        user_org = self.user.organization

        if doctor and doctor.organization_id != user_org.id:
            self.add_error("doctor", "Selected doctor is outside your organization.")

        if (
            doctor
            and getattr(self.user, "facility", None)
            and doctor.facility_id
            and doctor.facility_id != self.user.facility_id
        ):
            self.add_error("doctor", "Selected doctor is outside your facility.")

        out_start = cleaned_data.get("out_of_station_start_date")
        out_end = cleaned_data.get("out_of_station_end_date")
        is_available = cleaned_data.get("is_available")

        if out_start or out_end:
            if not out_start or not out_end:
                self.add_error(
                    "out_of_station_start_date",
                    "Both out of station start and end dates are required.",
                )
                self.add_error(
                    "out_of_station_end_date",
                    "Both out of station start and end dates are required.",
                )
            elif out_start > out_end:
                self.add_error(
                    "out_of_station_end_date",
                    "Out of station end date must be on or after the start date.",
                )

            if is_available:
                self.add_error(
                    "is_available",
                    "Out of station dates can only be used when the doctor is unavailable.",
                )

        if not day_values and not (out_start and out_end):
            self.add_error(
                "day_of_week",
                "Select a day of week or provide an out of station date range.",
            )

        if day_values:
            selected_days = [int(day) for day in day_values]
            if self.instance.pk and len(selected_days) > 1:
                self.add_error(
                    "day_of_week",
                    "You cannot select more than one day when editing an existing schedule.",
                )
            elif doctor and start_time and end_time:
                for day in selected_days:
                    schedule_qs = DoctorSchedule.objects.filter(
                        doctor=doctor,
                        day_of_week=day,
                    )
                    if self.instance.pk:
                        schedule_qs = schedule_qs.exclude(pk=self.instance.pk)

                    for schedule in schedule_qs:
                        if (
                            start_time < schedule.end_time
                            and end_time > schedule.start_time
                        ):
                            self.add_error(
                                "day_of_week",
                                "This schedule overlaps with an existing schedule for the selected day(s).",
                            )
                            break

        return cleaned_data

    def save(self, commit=True):
        day_values = self.cleaned_data.get("day_of_week")
        out_start = self.cleaned_data.get("out_of_station_start_date")
        out_end = self.cleaned_data.get("out_of_station_end_date")

        if self.instance.pk:
            if day_values:
                self.instance.day_of_week = int(day_values[0])
            elif out_start and out_end:
                self.instance.day_of_week = None
            return super().save(commit=commit)

        created_schedules = []
        if day_values:
            for day in [int(day) for day in day_values]:
                schedule = self.Meta.model(
                    doctor=self.cleaned_data["doctor"],
                    day_of_week=day,
                    start_time=self.cleaned_data["start_time"],
                    end_time=self.cleaned_data["end_time"],
                    out_of_station_start_date=out_start,
                    out_of_station_end_date=out_end,
                    is_available=self.cleaned_data["is_available"],
                )
                if commit:
                    schedule.save()
                created_schedules.append(schedule)
        else:
            schedule = self.Meta.model(
                doctor=self.cleaned_data["doctor"],
                day_of_week=None,
                start_time=self.cleaned_data["start_time"],
                end_time=self.cleaned_data["end_time"],
                out_of_station_start_date=out_start,
                out_of_station_end_date=out_end,
                is_available=self.cleaned_data["is_available"],
            )
            if commit:
                schedule.save()
            created_schedules.append(schedule)

        return created_schedules
