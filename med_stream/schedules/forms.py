from django import forms
from .models import Department, Doctor, OPDRoom, OPDSchedule, DoctorSchedule
from facilities.models import Facility


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
            "name",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["facility"].queryset = Facility.objects.none()
        if self.user and self.user.organization:
            self.fields["facility"].queryset = Facility.objects.filter(
                organization=self.user.organization,
                is_active=True,
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
    class Meta:
        model = OPDSchedule
        fields = [
            "doctor",
            "opd_room",
            "day_of_week",
            "start_time",
            "end_time",
            "is_available",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["doctor"].queryset = Doctor.objects.none()
        self.fields["opd_room"].queryset = OPDRoom.objects.none()

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
            self.add_error("opd_room", "Selected OPD room is outside your organization.")

        if (
            opd_room
            and getattr(self.user, "facility", None)
            and opd_room.facility_id
            and opd_room.facility_id != self.user.facility_id
        ):
            self.add_error("opd_room", "Selected OPD room is outside your facility.")

        return cleaned_data


# Doctor schedule.
class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = [
            "doctor",
            "day_of_week",
            "start_time",
            "end_time",
            "is_available",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["doctor"].queryset = Doctor.objects.none()

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

        return cleaned_data
