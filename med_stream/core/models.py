from django.db import models


# Base model.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Department model.
class Department(TimeStampedModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
