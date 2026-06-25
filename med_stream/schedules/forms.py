from datetime import timedelta

from django import forms
from django.utils.dateparse import parse_date
from .models import Department, Doctor, OPDRoom, OPDSchedule, DoctorSchedule
from facilities.models import Facility, Block, Floor
from django.utils import timezone


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


# Doctor schedule.
class DoctorScheduleForm(forms.ModelForm):

    class Meta:
        model = DoctorSchedule
        fields = [
            "doctor",
            "start_date",
            "end_date",
            "reason",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Enter reason (optional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Default empty queryset
        self.fields["doctor"].queryset = Doctor.objects.none()

        # Filter doctors by organization and facility
        if self.user and getattr(self.user, "organization", None):
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
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Skip org validation if user has no org
        if not self.user or not getattr(self.user, "organization", None):
            return cleaned_data

        user_org = self.user.organization

        # Organization validation
        if doctor and doctor.organization_id != user_org.id:
            self.add_error(
                "doctor",
                "Selected doctor is outside your organization.",
            )

        # Facility validation
        if (
            doctor
            and getattr(self.user, "facility", None)
            and doctor.facility_id
            and doctor.facility_id != self.user.facility_id
        ):
            self.add_error(
                "doctor",
                "Selected doctor is outside your facility.",
            )

        # Date validation
        if start_date and end_date:
            if start_date > end_date:
                self.add_error(
                    "end_date",
                    "End date must be on or after the start date.",
                )

            # Prevent overlapping records
            overlapping_qs = DoctorSchedule.objects.filter(
                doctor=doctor,
                start_date__lte=end_date,
                end_date__gte=start_date,
            )

            if self.instance.pk:
                overlapping_qs = overlapping_qs.exclude(pk=self.instance.pk)

            if overlapping_qs.exists():
                self.add_error(
                    "start_date",
                    ("This out-of-station period overlaps " "with an existing record."),
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

        return instance


# Add OPD schedule form.
class OPDScheduleForm(forms.ModelForm):
    opd_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="OPD date",
    )
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
        model = OPDSchedule
        fields = [
            "doctor",
            "opd_date",
            "opd_room",
            "start_time",
            "end_time",
            "is_available",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def _get_selected_weekdays(self):
        if self.data and hasattr(self.data, "getlist"):
            return [int(day) for day in self.data.getlist("day_of_week") if day]

        raw_values = self.data.get("day_of_week") if self.data else None
        if isinstance(raw_values, (list, tuple)):
            return [int(day) for day in raw_values if day]
        if raw_values:
            return [int(raw_values)]

        if self.instance and self.instance.pk and self.instance.day_of_week is not None:
            return [self.instance.day_of_week]

        return []

    def _get_selected_date(self):
        raw_value = self.data.get("opd_date") if self.data else None
        if raw_value:
            return parse_date(raw_value)
        if self.instance and self.instance.pk:
            return self.instance.opd_date
        return None

    def _get_next_occurrence_date(self, weekday):
        today = timezone.now().date()
        days_until = (weekday - today.weekday()) % 7
        return today + timedelta(days=days_until)

    def _get_out_of_station_doctor_ids_for_dates(self, doctor_qs, dates):
        if not dates:
            return set()

        out_of_station_ids = set()

        for target_date in dates:
            out_of_station_ids.update(
                DoctorSchedule.objects.filter(
                    doctor__in=doctor_qs,
                    start_date__lte=target_date,
                    end_date__gte=target_date,
                ).values_list("doctor_id", flat=True)
            )

        return out_of_station_ids

    def _get_out_of_station_day_labels(self, doctor, weekdays):
        unavailable_days = []

        for weekday in weekdays:
            target_date = self._get_next_occurrence_date(weekday)
            is_out_of_station = DoctorSchedule.objects.filter(
                doctor=doctor,
                start_date__lte=target_date,
                end_date__gte=target_date,
            ).exists()

            if is_out_of_station:
                unavailable_days.append(weekday)

        return unavailable_days

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["doctor"].queryset = Doctor.objects.none()
        self.fields["opd_room"].queryset = OPDRoom.objects.none()

        if self.instance and self.instance.pk:
            if self.instance.day_of_week is not None:
                self.fields["day_of_week"].initial = [self.instance.day_of_week]
            self.fields["opd_date"].initial = self.instance.opd_date

        if self.user and self.user.organization:
            doctor_qs = Doctor.objects.filter(
                organization=self.user.organization,
                is_active=True,
            )

            if getattr(self.user, "facility", None):
                doctor_qs = doctor_qs.filter(facility=self.user.facility)

            selected_date = self._get_selected_date()
            if selected_date:
                out_of_station_ids = self._get_out_of_station_doctor_ids_for_dates(
                    doctor_qs,
                    [selected_date],
                )
            else:
                selected_weekdays = set(self._get_selected_weekdays())
                out_of_station_ids = self._get_out_of_station_doctor_ids_for_dates(
                    doctor_qs,
                    [self._get_next_occurrence_date(weekday) for weekday in selected_weekdays],
                )

            doctor_qs = doctor_qs.exclude(id__in=out_of_station_ids)

            self.fields["doctor"].queryset = doctor_qs

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
        opd_date = cleaned_data.get("opd_date")
        opd_room = cleaned_data.get("opd_room")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        day_values = cleaned_data.get("day_of_week") or []

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

        if not opd_date and not day_values:
            self.add_error("opd_date", "Select an OPD date or at least one weekday.")

        if opd_date and day_values:
            selected_days = [int(day) for day in day_values]
            if opd_date.weekday() not in selected_days:
                self.add_error(
                    "day_of_week",
                    "When an OPD date is selected, its weekday must also be selected.",
                )

        if doctor:
            if opd_date:
                unavailable_days = self._get_out_of_station_doctor_ids_for_dates(
                    Doctor.objects.filter(pk=doctor.pk),
                    [opd_date],
                )
                if unavailable_days:
                    self.add_error(
                        "doctor",
                        "Selected doctor is out of station on the selected date.",
                    )
            else:
                selected_weekdays = set(self._get_selected_weekdays())
                if selected_weekdays:
                    unavailable_days = self._get_out_of_station_day_labels(
                        doctor,
                        selected_weekdays,
                    )
                    if unavailable_days:
                        day_labels = [
                            label
                            for value, label in self.fields["day_of_week"].choices
                            if int(value) in unavailable_days
                        ]
                        self.add_error(
                            "day_of_week",
                            (
                                "Selected doctor is out of station for: "
                                f"{', '.join(day_labels)}."
                            ),
                        )

        if day_values and not opd_date:
            selected_days = [int(day) for day in day_values]

            if self.instance.pk and len(selected_days) > 1:
                self.add_error(
                    "day_of_week",
                    "You cannot select more than one day when editing an existing schedule.",
                )
            elif doctor and opd_room and start_time and end_time:
                for day in selected_days:
                    schedule_qs = OPDSchedule.objects.filter(
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
        if self.instance.pk:
            self.instance.opd_date = self.cleaned_data.get("opd_date")
            day_values = self.cleaned_data.get("day_of_week")
            if self.instance.opd_date:
                self.instance.day_of_week = self.instance.opd_date.weekday()
            elif day_values:
                self.instance.day_of_week = int(day_values[0])
            return super().save(commit=commit)

        created_schedules = []
        opd_date = self.cleaned_data.get("opd_date")

        if opd_date:
            schedule = self.Meta.model(
                doctor=self.cleaned_data["doctor"],
                opd_date=opd_date,
                opd_room=self.cleaned_data["opd_room"],
                day_of_week=opd_date.weekday(),
                start_time=self.cleaned_data["start_time"],
                end_time=self.cleaned_data["end_time"],
                is_available=self.cleaned_data["is_available"],
            )
            if commit:
                schedule.save()
            created_schedules.append(schedule)
            return created_schedules

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
