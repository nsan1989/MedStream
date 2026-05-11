from django.db import models


# Device type choices.
class DeviceType(models.TextChoices):
    TV = "TV", "Television"
    KIOSK = "KIOSK", "Kiosk"
    LED_WALL = "LED_WALL", "LED Wall"
    OTHER = "OTHER", "Other"


# Device status choices.
class DeviceStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    MAINTENANCE = "MAINTENANCE", "Maintenance"
    DECOMMISSIONED = "DECOMMISSIONED", "Decommissioned"


# Orientation choices.
class OrientationChoices(models.TextChoices):
    PORTRAIT = "PORTRAIT", "Portrait"
    LANDSCAPE = "LANDSCAPE", "Landscape"


# Log type choices.
class LogType(models.TextChoices):
    ERROR = "ERROR", "Error"
    WARNING = "WARNING", "Warning"
    INFO = "INFO", "Info"
