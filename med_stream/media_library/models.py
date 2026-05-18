import uuid
from pathlib import Path


from django.db import models
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel
from accounts.models import CustomUser
from .enums import MediaAssetType
from organizations.models import Organization
from facilities.models import Facility


# Media asset model.
class MediaAsset(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="media_organization",
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="media_facility",
    )
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "title"],
                name="uniq_media_asset_title_per_organization",
            )
        ]

    def clean(self):
        super().clean()

        if self.organization and self.facility:
            if self.facility.organization_id != self.organization_id:
                raise ValidationError(
                    {
                        "facility": (
                            "Facility must belong to the selected organization."
                        )
                    }
                )

        if self.uploaded_by and self.organization:
            if self.uploaded_by.organization_id != self.organization_id:
                raise ValidationError(
                    {
                        "uploaded_by": "Uploader must belong to the selected organization."
                    }
                )

        if self.tags is not None:
            if not isinstance(self.tags, list):
                raise ValidationError({"tags": "Tags must be a list of strings."})
            for tag in self.tags:
                if not isinstance(tag, str) or not tag.strip():
                    raise ValidationError(
                        {"tags": "Each tag must be a non-empty string."}
                    )

        if self.file:
            extension = Path(self.file.name).suffix.lower()
            allowed_extensions = {
                MediaAssetType.VIDEO: {".mp4", ".mov", ".webm", ".mkv", ".avi"},
                MediaAssetType.AUDIO: {".mp3", ".wav", ".aac", ".ogg", ".m4a"},
                MediaAssetType.IMAGE: {".jpg", ".jpeg", ".png", ".gif", ".webp"},
                MediaAssetType.PDF: {".pdf"},
                MediaAssetType.HTML: {".html", ".htm"},
            }
            valid_exts = allowed_extensions.get(self.media_type, set())
            if extension not in valid_exts:
                raise ValidationError(
                    {
                        "file": (
                            f"File extension '{extension or '[none]'}' is not valid "
                            f"for media type '{self.media_type}'."
                        )
                    }
                )

        if self.media_type in [MediaAssetType.VIDEO, MediaAssetType.AUDIO]:
            if self.duration is None:
                raise ValidationError(
                    {"duration": "Duration is required for video and audio assets."}
                )
            if self.duration.total_seconds() <= 0:
                raise ValidationError({"duration": "Duration must be greater than zero."})
        elif self.duration is not None and self.duration.total_seconds() <= 0:
            raise ValidationError({"duration": "Duration must be greater than zero."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title
