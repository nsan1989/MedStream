from django.db import models
from core.models import TimeStampedModel
from .enums import EmergencyAlertLevel
from accounts.models import CustomUser


# Emergency model.
class Emergency(TimeStampedModel):
    title = models.CharField(max_length=255)
    message = models.TextField()
    alert_level = models.CharField(
        max_length=20,
        choices=EmergencyAlertLevel.choices,
        default=EmergencyAlertLevel.INFO,
    )
    background_color = models.CharField(max_length=7, default="#FFFFFF")
    text_color = models.CharField(max_length=7, default="#000000")
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="emergencies"
    )

    def __str__(self):
        return self.title
