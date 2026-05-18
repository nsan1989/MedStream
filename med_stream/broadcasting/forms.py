from django import forms

from devices.models import Device
from media_library.models import MediaAsset
from playlists.models import Playlist


class DevicePlaybackForm(forms.Form):
    device = forms.ModelChoiceField(queryset=Device.objects.none(), required=True)
    media_asset = forms.ModelChoiceField(
        queryset=MediaAsset.objects.none(), required=False, empty_label="Select Media Asset"
    )
    playlist = forms.ModelChoiceField(
        queryset=Playlist.objects.none(), required=False, empty_label="Select Playlist"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.organization:
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

            if self.user.role == "STAFF":
                device_qs = device_qs.filter(facility=self.user.facility)
                media_qs = media_qs.filter(facility=self.user.facility)
                playlist_qs = playlist_qs.filter(facility=self.user.facility)

            self.fields["device"].queryset = device_qs.order_by("name")
            self.fields["media_asset"].queryset = media_qs.order_by("title")
            self.fields["playlist"].queryset = playlist_qs.order_by("name")

    def clean(self):
        cleaned_data = super().clean()
        media_asset = cleaned_data.get("media_asset")
        playlist = cleaned_data.get("playlist")

        if not media_asset and not playlist:
            raise forms.ValidationError("Select either a media asset or a playlist.")

        if media_asset and playlist:
            raise forms.ValidationError("Select only one source: media asset or playlist.")

        return cleaned_data
