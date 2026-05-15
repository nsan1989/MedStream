import uuid


from django.db import models
from django.core.exceptions import ValidationError
from organizations.models import Organization
from core.models import TimeStampedModel
from accounts.models import CustomUser


# Facilities model.
class Facility(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="facilities"
    )
    facility_admin = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="admin_facility",
        null=True,
        blank=True,
        limit_choices_to={"role": "ADMIN"},
    )
    facility_staff = models.ManyToManyField(
        CustomUser,
        related_name="staff_facility",
        blank=True,
        limit_choices_to={"role": "STAFF"},
    )
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


# Block model.
class Block(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="blocks", null=True, blank=True
    )
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Block"
        verbose_name_plural = "Blocks"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["facility", "name"], name="unique_block_per_facility"
            )
        ]

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
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Floor"
        verbose_name_plural = "Floors"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["block", "name"], name="unique_floor_per_block"
            )
        ]

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
