import uuid

from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.utils.text import slugify
from .enums import OrganizationType, SubscriptionStatus
from subscriptions.models import SubscriptionPlan
from core.models import TimeStampedModel


# Organization model.
class Organization(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    organization_type = models.CharField(
        max_length=50,
        choices=OrganizationType.choices,
        default=OrganizationType.HOSPITAL,
    )
    registration_number = models.CharField(
        max_length=100, unique=True, blank=True, null=True
    )
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organizations_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organizations_updated",
    )

    class Meta:
        db_table = "organizations"
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Organization.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Organization branding model.
class OrganizationBranding(TimeStampedModel):
    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name="branding"
    )
    logo = models.ImageField(
        upload_to="organizations/branding/logos/", blank=True, null=True
    )
    favicon = models.ImageField(
        upload_to="organizations/branding/favicons/", blank=True, null=True
    )
    primary_color = models.CharField(max_length=7, blank=True, null=True)
    secondary_color = models.CharField(max_length=7, blank=True, null=True)
    login_banner = models.ImageField(
        upload_to="organizations/branding/login_banners/", blank=True, null=True
    )

    class Meta:
        db_table = "organization_branding"
        verbose_name = "Organization Branding"
        verbose_name_plural = "Organization Branding"

    def __str__(self):
        return f"{self.organization.name} Branding"


# Organization subscription model.
class OrganizationSubscription(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="subscriptions"
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.PROTECT, null=True, blank=True
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.INACTIVE,
    )
    auto_renew = models.BooleanField(default=False)
    is_trial = models.BooleanField(default=False)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "organization_subscriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.subscription_plan.name}"

    @property
    def is_expired(self):
        return timezone.now().date() > self.end_date

    @classmethod
    def create_free_trial(cls, organization):
        trial_plan = SubscriptionPlan.objects.get(billing_cycle="FREE_TRIAL")
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=10)

        return cls.objects.create(
            organization=organization,
            subscription_plan=trial_plan,
            start_date=start_date,
            end_date=end_date,
            status="TRIAL",
            is_trial=True,
            amount_paid=0,
        )
