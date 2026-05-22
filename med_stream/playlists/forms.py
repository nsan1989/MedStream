from django import forms
from .models import Playlist, PlaylistItem
from media_library.models import MediaAsset
from schedules.models import OPDSchedule, DoctorSchedule


# Playlist form.
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ["name", "facility", "description", "is_active"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.organization:
            self.fields["facility"].queryset = self.user.organization.facilities.filter(
                is_active=True
            ).order_by("name")
        else:
            self.fields["facility"].queryset = self.fields["facility"].queryset.none()

    def save(self, commit=True):
        playlist = super().save(commit=False)
        if self.user:
            playlist.created_by = self.user
            playlist.organization = self.user.organization
            if self.user.role == "STAFF":
                playlist.facility = self.user.facility
        if commit:
            playlist.save()
        return playlist


class PlaylistItemForm(forms.ModelForm):
    media_assets = forms.ModelMultipleChoiceField(
        queryset=MediaAsset.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    opd_schedules = forms.ModelMultipleChoiceField(
        queryset=OPDSchedule.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    doctor_schedules = forms.ModelMultipleChoiceField(
        queryset=DoctorSchedule.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = PlaylistItem
        fields = [
            "playlist",
            "duration",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.playlist = kwargs.pop("playlist", None)

        super().__init__(*args, **kwargs)

        self.fields["duration"].required = False

        # Playlist queryset
        self.fields["playlist"].queryset = Playlist.objects.none()

        if self.playlist is not None:
            self.fields["playlist"].queryset = Playlist.objects.filter(
                pk=self.playlist.pk
            )
            self.fields["playlist"].initial = self.playlist

        elif self.user and self.user.organization:
            queryset = Playlist.objects.filter(organization=self.user.organization)

            if self.user.role == "STAFF":
                queryset = queryset.filter(facility=self.user.facility)

            self.fields["playlist"].queryset = queryset.order_by("name")

        # Media queryset
        if self.user and self.user.organization:
            media_qs = MediaAsset.objects.filter(
                organization=self.user.organization,
                is_active=True,
            )

            if self.user.role == "STAFF":
                media_qs = media_qs.filter(facility=self.user.facility)

            self.fields["media_assets"].queryset = media_qs.order_by("title")

        # OPD queryset
        opd_qs = OPDSchedule.objects.none()

        if self.user and self.user.organization:
            opd_qs = OPDSchedule.objects.filter(
                doctor__organization=self.user.organization,
                opd_room__organization=self.user.organization,
            ).select_related("doctor", "doctor__facility", "opd_room")

            if self.user.role == "STAFF":
                opd_qs = opd_qs.filter(
                    doctor__facility=self.user.facility,
                    opd_room__facility=self.user.facility,
                )

        self.fields["opd_schedules"].queryset = opd_qs.order_by(
            "day_of_week", "start_time"
        )

        # Doctor queryset
        doctor_qs = DoctorSchedule.objects.none()

        if self.user and self.user.organization:
            doctor_qs = OPDSchedule.objects.filter(
                doctor__organization=self.user.organization,
            ).select_related("doctor", "doctor__facility")

            if self.user.role == "STAFF":
                doctor_qs = doctor_qs.filter(
                    doctor__facility=self.user.facility,
                )

        self.fields["doctor_schedules"].queryset = doctor_qs.order_by(
            "day_of_week", "start_time"
        )

    def clean(self):
        cleaned_data = super().clean()

        media_assets = cleaned_data.get("media_assets")
        opd_schedules = cleaned_data.get("opd_schedules")
        doctor_schedules = cleaned_data.get("doctor_schedules")
        duration = cleaned_data.get("duration")

        # Safe selection checks
        has_media = media_assets is not None and media_assets.exists()

        has_opd = opd_schedules is not None and opd_schedules.exists()

        has_doctor = doctor_schedules is not None and doctor_schedules.exists()

        # Must select at least one
        if not (has_media or has_opd or has_doctor):
            raise forms.ValidationError(
                "Select at least one of media asset, OPD schedule, or doctor schedule."
            )

        # Duration required only for media
        if has_media:
            if not duration or duration <= 0:
                self.add_error(
                    "duration", "Duration is required when media is selected."
                )

        return cleaned_data
