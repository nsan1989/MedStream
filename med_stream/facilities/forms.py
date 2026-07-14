from django import forms
from .models import Block, Floor, Facility
from accounts.models import CustomUser


# Staff form.
class StaffForm(forms.ModelForm):

    facility = forms.ModelChoiceField(
        queryset=Facility.objects.none(),
        empty_label="Select Facility",
    )

    class Meta:
        model = Facility
        fields = [
            "facility_staff",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["facility"].queryset = Facility.objects.filter(
                organization=user.organization,
                is_active=True,
            )

            self.fields["facility_staff"].queryset = CustomUser.objects.filter(
                organization=user.organization,
                role="STAFF",
                is_active=True,
            )

            self.fields["facility_staff"].label = "Select Staff Members"


# Facility form.
class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = [
            "name",
        ]


# Block form.
class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = [
            "facility",
            "name",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields["facility"].queryset = Facility.objects.filter(
                organization=user.organization,
                is_active=True,
            )


# Floor form.
class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ["block", "name"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        print(user)

        if user:
            if user.role == "ADMIN":
                facilities = Facility.objects.filter(
                    organization=user.organization, is_active=True
                )
            elif user.role == "STAFF":
                facilities = Facility.objects.filter(
                    facility_staff=user, is_active=True
                )
            else:
                facilities = Facility.objects.none()

            print("Facilities:", list(facilities.values("id", "name")))

            blocks = Block.objects.filter(
                facility__in=facilities,
                is_active=True,
            )

            print("Blocks:", list(blocks.values("id", "name")))

            self.fields["block"].queryset = Block.objects.filter(
                facility__in=facilities
            )
