import uuid


from django.db import models
from core.models import TimeStampedModel
from facilities.models import Floor
from .enums import DeviceType, DeviceStatus, OrientationChoices, LogType


# Device model.
class Device(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="devices")
    device_type = models.CharField(
        max_length=20, choices=DeviceType.choices, default=DeviceType.TV
    )
    status = models.CharField(
        max_length=20, choices=DeviceStatus.choices, default=DeviceStatus.ACTIVE
    )
    orientation = models.CharField(
        max_length=20,
        choices=OrientationChoices.choices,
        default=OrientationChoices.LANDSCAPE,
    )
    resolution_width = models.IntegerField(default=1920)
    resolution_height = models.IntegerField(default=1080)
    ip_address = models.GenericIPAddressField(protocol="IPv4", unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.device_type}) - {self.status}"


# Device log model.
class DeviceLog(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="logs")
    log_type = models.CharField(
        max_length=20, choices=LogType.choices, default=LogType.INFO
    )
    message = models.TextField()
    metadata = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        return f"{self.log_type} - {self.message[:50]}..."
