from django import forms

from devices.models import Device
from media_library.models import MediaAsset
from playlists.models import Playlist
from schedules.models import DoctorSchedule, OPDSchedule
from django.utils import timezone
from facilities.models import Block, Floor


class DevicePlaybackForm(forms.Form):
    block = forms.ModelChoiceField(
        queryset=Block.objects.none(),
        required=False,
        empty_label="Select Block",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "id_block",
            }
        ),
    )
    floor = forms.ModelChoiceField(
        queryset=Floor.objects.none(),
        required=False,
        empty_label="Select Floor",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "id_floor",
            }
        ),
    )
    select_all_devices = forms.BooleanField(
        required=False,
        label="Select All Devices",
    )
    device = forms.ModelMultipleChoiceField(
        queryset=Device.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
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

            device_qs = Device.objects.filter(
                facility__organization=self.user.organization,
                is_active=True,
            )
            block_qs = Block.objects.filter(
                facility__organization=self.user.organization,
                is_active=True,
            )
            floor_qs = Floor.objects.filter(
                block__facility__organization=self.user.organization,
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
                block_qs = block_qs.filter(facility=self.user.facility)
                floor_qs = floor_qs.filter(block__facility=self.user.facility)
                media_qs = media_qs.filter(facility=self.user.facility)
                playlist_qs = playlist_qs.filter(facility=self.user.facility)
                doctor_schedule_qs = doctor_schedule_qs.filter(
                    doctor__facility=self.user.facility
                )

            selected_block = self.data.get("block")
            selected_floor = self.data.get("floor")

            if selected_block:
                floor_qs = floor_qs.filter(block_id=selected_block)

                device_qs = device_qs.filter(block_id=selected_block)

            if selected_floor:
                device_qs = device_qs.filter(floor_id=selected_floor)

            self.fields["block"].queryset = block_qs.order_by("name")
            self.fields["floor"].queryset = floor_qs.order_by("name")
            self.fields["device"].queryset = device_qs.order_by("name")
            self.fields["media_asset"].queryset = media_qs.order_by("title")
            self.fields["playlist"].queryset = playlist_qs.order_by("name")
            self.fields["doctor_schedule"].queryset = doctor_schedule_qs.order_by(
                "doctor__name", "start_date"
            )

    def clean(self):
        cleaned_data = super().clean()
        select_all_devices = cleaned_data.get("select_all_devices")
        devices = cleaned_data.get("device")
        block = cleaned_data.get("block")
        floor = cleaned_data.get("floor")
        media_asset = cleaned_data.get("media_asset")
        playlist = cleaned_data.get("playlist")
        doctor_schedule = cleaned_data.get("doctor_schedule")
        play_today_opd = cleaned_data.get("play_today_opd")

        if select_all_devices:
            device_qs = self.fields["device"].queryset
            if block:
                device_qs = device_qs.filter(block=block)

            if floor:
                device_qs = device_qs.filter(floor=floor)

            devices = device_qs
            cleaned_data["device"] = devices

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
