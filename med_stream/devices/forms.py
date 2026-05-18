from django import forms
from .models import Device
from facilities.models import Facility, Floor, Block


# Device form.
class DeviceForm(forms.ModelForm):

    facility = forms.ModelChoiceField(
        queryset=Facility.objects.none(),
        required=True,
    )

    block = forms.ModelChoiceField(
        queryset=Block.objects.none(),
        required=True,
    )

    floor = forms.ModelChoiceField(
        queryset=Floor.objects.none(),
        required=True,
    )

    class Meta:
        model = Device
        fields = [
            "name",
            "facility",
            "block",
            "floor",
            "device_type",
            "orientation",
            "resolution_width",
            "resolution_height",
            "ip_address",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter device name",
                }
            ),
            "resolution_width": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "resolution_height": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "ip_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "192.168.1.10",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Add bootstrap class
        for field in self.fields.values():
            field.help_text = None

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-control"
        if user:
            self.fields["facility"].queryset = Facility.objects.filter(
                organization=user.organization
            )

            self.fields["block"].queryset = Block.objects.none()

            self.fields["floor"].queryset = Floor.objects.none()

            if "facility" in self.data:
                try:
                    facility_id = self.data.get("facility")

                    self.fields["block"].queryset = Block.objects.filter(
                        facility_id=facility_id,
                        facility__organization=user.organization,
                    )
                except (
                    ValueError,
                    TypeError,
                ):
                    pass

            if "block" in self.data:
                try:
                    block_id = self.data.get("block")

                    self.fields["floor"].queryset = Floor.objects.filter(
                        block_id=block_id,
                        block__facility__organization=user.organization,
                    )
                except (
                    ValueError,
                    TypeError,
                ):
                    pass

    def save(self, commit=True):
        device = super().save(commit=False)
        device.floor = self.cleaned_data["floor"]
        if commit:
            device.save()
        return device
