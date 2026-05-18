from django import forms

from facilities.models import Facility

from .models import MediaAsset


class MediaAssetForm(forms.ModelForm):
    class Meta:
        model = MediaAsset
        fields = [
            "title",
            "facility",
            "description",
            "media_type",
            "file",
            "thumbnail",
            "duration",
            "tags",
            "is_active",
            "is_public",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "tags": forms.TextInput(
                attrs={"placeholder": '["news", "morning", "cardiology"]'}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["facility"].queryset = Facility.objects.none()
        if self.user and self.user.organization:
            self.fields["facility"].queryset = Facility.objects.filter(
                organization=self.user.organization,
                is_active=True,
            ).order_by("name")

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean_facility(self):
        facility = self.cleaned_data.get("facility")
        if not facility:
            return facility

        if self.user and self.user.organization:
            if facility.organization_id != self.user.organization_id:
                raise forms.ValidationError(
                    "Selected facility is outside your organization."
                )
        return facility

    def save(self, commit=True):
        media_asset = super().save(commit=False)

        if self.user:
            media_asset.uploaded_by = self.user
            if self.user.organization:
                media_asset.organization = self.user.organization

        if commit:
            media_asset.save()

        return media_asset
