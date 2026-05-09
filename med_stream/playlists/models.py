from django.db import models
from core.models import TimeStampedModel
from accounts.models import CustomUser
from media_library.models import MediaAsset


# Playlist model.
class Playlist(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="playlists",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

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

    def __str__(self):
        return f"{self.playlist.name} - {self.media_asset.title}"
