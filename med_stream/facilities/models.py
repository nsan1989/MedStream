import uuid


from django.db import models
from organizations.models import Organization
from core.models import TimeStampedModel


# Block model.
class Block(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Block"
        verbose_name_plural = "Blocks"
        ordering = ["name"]

    def __str__(self):
        return self.name


# Floor model.
class Floor(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="locations")

    class Meta:
        verbose_name = "Floor"
        verbose_name_plural = "Floors"
        ordering = ["name"]

    def __str__(self):
        return self.name


# Facilities model.
class Facility(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="facilities"
    )
    blocks = models.ManyToManyField(Block, related_name="facilities", blank=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"
        ordering = ["name"]

    def __str__(self):
        return self.name
