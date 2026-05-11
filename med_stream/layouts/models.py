from django.db import models
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel
from .enums import LayoutType, ZoneType
from accounts.models import CustomUser


# Layout model.
class Layout(TimeStampedModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="layouts",
    )
    layout_type = models.CharField(
        max_length=50, choices=LayoutType.choices, default=LayoutType.LANDSCAPE
    )
    resoluttion_width = models.IntegerField(default=1920)
    resoluttion_height = models.IntegerField(default=1080)

    background_color = models.CharField(max_length=7, default="#000000")
    layout_config = models.JSONField(default=dict)

    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="created_layouts"
    )
    updated_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="updated_layouts"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="uniq_layout_name_per_organization",
            )
        ]

    def clean(self):
        super().clean()

        if self.created_by and self.organization:
            if self.created_by.organization_id != self.organization_id:
                raise ValidationError(
                    {"created_by": "Creator must belong to the selected organization."}
                )

        if self.updated_by and self.organization:
            if self.updated_by.organization_id != self.organization_id:
                raise ValidationError(
                    {"updated_by": "Updater must belong to the selected organization."}
                )

    def __str__(self):
        return self.name


# Layout zone model.
class LayoutZone(TimeStampedModel):
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE, related_name="zones")
    name = models.CharField(max_length=255)
    zone_type = models.CharField(
        max_length=50, choices=ZoneType.choices, default=ZoneType.VIDEO
    )
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    z_index = models.IntegerField(default=1)
    config = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.layout.name} - {self.name}"
