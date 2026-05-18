from django import forms
from .models import Playlist, PlaylistItem
from media_library.models import MediaAsset


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


# Playlist item form.
class PlaylistItemForm(forms.ModelForm):
    class Meta:
        model = PlaylistItem
        fields = ["playlist", "media_asset", "order", "duration"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.playlist = kwargs.pop("playlist", None)
        super().__init__(*args, **kwargs)

        self.fields["playlist"].queryset = Playlist.objects.none()
        self.fields["media_asset"].queryset = MediaAsset.objects.none()

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

        if self.user and self.user.organization:
            media_qs = MediaAsset.objects.filter(
                organization=self.user.organization,
                is_active=True,
            )
            if self.user.role == "STAFF":
                media_qs = media_qs.filter(facility=self.user.facility)
            self.fields["media_asset"].queryset = media_qs.order_by("title")
