from django.db import models


# Layout type choices.
class LayoutType(models.TextChoices):
    LANDSCAPE = "LANDSCAPE", "Landscape"
    PORTRAIT = "PORTRAIT", "Portrait"


# Zone type choices.
class ZoneType(models.TextChoices):
    VIDEO = "VIDEO", "Video"
    IMAGE = "IMAGE", "Image"
    TEXT = "TEXT", "Text"
    QUEUE = "QUEUE", "Queue"
    DOCTOR = "DOCTOR", "Doctor"
    EMERGENCY = "EMERGENCY", "Emergency"
    CLOCK = "CLOCK", "Clock"
    WEATHER = "WEATHER", "Weather"
    NEWS = "NEWS", "News"
