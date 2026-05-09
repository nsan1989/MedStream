import uuid


from django.db import models
from core.models import TimeStampedModel
from accounts.models import CustomUser
from .enums import MediaAssetType


# Media asset model.
class MediaAsset(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    media_type = models.CharField(
        max_length=20, choices=MediaAssetType.choices, default=MediaAssetType.VIDEO
    )
    file = models.FileField(upload_to="media_assets/")
    thumbnail = models.ImageField(upload_to="media_thumbnails/", blank=True, null=True)
    duration = models.DurationField(
        blank=True,
        null=True,
        help_text="Duration of the media asset (applicable for videos and audio files)",
    )
    tags = models.JSONField(
        blank=True, null=True, help_text="List of tags associated with the media asset"
    )
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_media_assets",
    )
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.title
