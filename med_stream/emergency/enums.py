from django.db import models


# Emergency alert level choices.
class EmergencyAlertLevel(models.TextChoices):
    INFO = "INFO", "Information"
    WARNING = "WARNING", "Warning"
    CRITICAL = "CRITICAL", "Critical"
