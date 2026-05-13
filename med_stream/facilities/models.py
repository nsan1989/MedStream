import uuid


from django.db import models
from django.core.exceptions import ValidationError
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

    def clean(self):
        super().clean()

        name_qs = Block.objects.filter(name__iexact=self.name)
        if self.pk:
            name_qs = name_qs.exclude(pk=self.pk)

        if name_qs.exists():
            raise ValidationError({"name": "A block with this name already exists."})

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

    def clean(self):
        super().clean()
        floor_qs = Floor.objects.filter(
            name__iexact=self.name,
            block__name__iexact=self.block.name,
        )
        if self.pk:
            floor_qs = floor_qs.exclude(pk=self.pk)
        if floor_qs.exists():
            raise ValidationError(
                {"name": "A floor with this name already exists in the same block."}
            )

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
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"
        ordering = ["name"]

    def clean(self):
        super().clean()
        facility_qs = Facility.objects.filter(
            name__iexact=self.name,
            phone_number__iexact=self.phone_number,
        )
        if self.pk:
            facility_qs = facility_qs.exclude(pk=self.pk)
        if facility_qs.exists():
            raise ValidationError(
                {"name": "A facility with this name and phone number already exists."}
            )

    def __str__(self):
        return self.name
