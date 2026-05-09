from django.db import models


# Media asset type choices.
class MediaAssetType(models.TextChoices):
    VIDEO = "VIDEO", "Video"
    AUDIO = "AUDIO", "Audio"
    IMAGE = "IMAGE", "Image"
    PDF = "PDF", "PDF"
    HTML = "HTML", "HTML"
