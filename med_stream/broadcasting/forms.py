from django import forms

from devices.models import Device
from media_library.models import MediaAsset
from playlists.models import Playlist
from schedules.models import DoctorSchedule, OPDSchedule
from django.utils import timezone


class DevicePlaybackForm(forms.Form):
    device = forms.ModelMultipleChoiceField(
        queryset=Device.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
    )
    media_asset = forms.ModelChoiceField(
        queryset=MediaAsset.objects.none(),
        required=False,
        empty_label="Select Media Asset",
    )
    playlist = forms.ModelChoiceField(
        queryset=Playlist.objects.none(), required=False, empty_label="Select Playlist"
    )
    doctor_schedule = forms.ModelChoiceField(
        queryset=DoctorSchedule.objects.none(),
        required=False,
        empty_label="Select Doctor Schedule",
    )
    play_today_opd = forms.BooleanField(
        required=False,
        label="Play Today's OPD Schedule",
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.organization:

            today = timezone.now().date()
            current_day = today.weekday()

            device_qs = Device.objects.filter(
                facility__organization=self.user.organization,
                is_active=True,
            )
            media_qs = MediaAsset.objects.filter(
                organization=self.user.organization,
                is_active=True,
            )
            playlist_qs = Playlist.objects.filter(
                organization=self.user.organization,
                is_active=True,
            )
            doctor_schedule_qs = DoctorSchedule.objects.filter(
                doctor__organization=self.user.organization,
                start_date__lte=today,
                end_date__gte=today,
                doctor__is_active=True,
            ).select_related("doctor")

            if self.user.role == "STAFF":
                device_qs = device_qs.filter(facility=self.user.facility)
                media_qs = media_qs.filter(facility=self.user.facility)
                playlist_qs = playlist_qs.filter(facility=self.user.facility)
                doctor_schedule_qs = doctor_schedule_qs.filter(
                    doctor__facility=self.user.facility
                )

            self.fields["device"].queryset = device_qs.order_by("name")
            self.fields["media_asset"].queryset = media_qs.order_by("title")
            self.fields["playlist"].queryset = playlist_qs.order_by("name")
            self.fields["doctor_schedule"].queryset = doctor_schedule_qs.order_by(
                "doctor__name", "start_date"
            )

    def clean(self):
        cleaned_data = super().clean()
        devices = cleaned_data.get("device")
        media_asset = cleaned_data.get("media_asset")
        playlist = cleaned_data.get("playlist")
        doctor_schedule = cleaned_data.get("doctor_schedule")
        play_today_opd = cleaned_data.get("play_today_opd")

        if not devices or not devices.exists():
            raise forms.ValidationError("Select at least one device.")

        selected_sources = sum(
            [
                bool(media_asset),
                bool(playlist),
                bool(doctor_schedule),
                bool(play_today_opd),
            ]
        )

        if selected_sources == 0:
            raise forms.ValidationError(
                "Select either a media asset, playlist, doctor schedule, or OPD schedule."
            )

        if selected_sources > 1:
            raise forms.ValidationError("Select only one source.")

        return cleaned_data
