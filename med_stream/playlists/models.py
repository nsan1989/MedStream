from django.db import models
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel
from accounts.models import CustomUser
from media_library.models import MediaAsset


# Playlist model.
class Playlist(TimeStampedModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="playlists",
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="playlists",
    )
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="playlists",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="uniq_playlist_name_per_organization",
            )
        ]

    def clean(self):
        super().clean()

        if self.created_by and not self.organization:
            raise ValidationError(
                {
                    "organization": (
                        "Organization is required when a creator is assigned."
                    )
                }
            )

        if self.created_by and self.organization:
            if self.created_by.organization_id != self.organization_id:
                raise ValidationError(
                    {"created_by": "Creator must belong to the selected organization."}
                )

        if self.organization and self.facility:
            if self.facility.organization_id != self.organization_id:
                raise ValidationError(
                    {
                        "facility": (
                            "Facility must belong to the selected organization."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Playlist item model.
class PlaylistItem(TimeStampedModel):
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name="items",
    )
    media_asset = models.ForeignKey(
        MediaAsset,
        on_delete=models.CASCADE,
        related_name="playlist_items",
    )
    order = models.PositiveIntegerField(default=0)
    duration = models.IntegerField(help_text="Duration in seconds")

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["playlist", "order"],
                name="uniq_playlist_item_order_per_playlist",
            )
        ]

    def clean(self):
        super().clean()

        if self.order < 0:
            raise ValidationError({"order": "Order must be zero or greater."})

        if self.duration <= 0:
            raise ValidationError({"duration": "Duration must be greater than zero."})

        playlist_org_id = self.playlist.organization_id
        media_org_id = self.media_asset.organization_id
        if playlist_org_id and media_org_id and playlist_org_id != media_org_id:
            raise ValidationError(
                {
                    "media_asset": (
                        "Media asset must belong to the same organization as the playlist."
                    )
                }
            )

        if self.playlist.facility_id and self.media_asset.facility_id:
            if self.media_asset.facility_id != self.playlist.facility_id:
                raise ValidationError(
                    {
                        "media_asset": (
                            "Media asset must belong to the same facility as the playlist."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.playlist.name} - {self.media_asset.title}"
