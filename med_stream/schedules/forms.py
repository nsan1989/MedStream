from django import forms
from .models import Department, Doctor, OPDSchedule, DoctorSchedule
from organizations.models import Organization
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
