from django.db import models


# Broadcast status choices.
class BroadcastStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    ONGOING = "ONGOING", "Ongoing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    INTERRUPTED = "INTERRUPTED", "Interrupted"
