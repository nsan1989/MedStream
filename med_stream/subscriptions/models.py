import uuid

from django.db import models
from django.utils import timezone
from datetime import timedelta
from .enums import SubscriptionChoices
from core.models import TimeStampedModel


# Subscription plan.
class SubscriptionPlan(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    billing_cycle = models.CharField(
        max_length=20,
        choices=SubscriptionChoices.choices,
        default=SubscriptionChoices.FREE_TRIAL,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    trial_days = models.PositiveIntegerField(default=0)
    max_users = models.PositiveIntegerField(default=1)
    max_facilities = models.PositiveIntegerField(default=1)
    max_storage = models.PositiveIntegerField(default=1024)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subscription_plans"
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} ({self.billing_cycle})"
