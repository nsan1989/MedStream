import uuid

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.utils.text import slugify
from .enums import OrganizationType, SubscriptionStatus
from subscriptions.models import SubscriptionPlan
from core.models import TimeStampedModel
from accounts.models import CustomUser


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

    def clean(self):
        super().clean()

        name_qs = Organization.objects.filter(name__iexact=self.name)
        if self.pk:
            name_qs = name_qs.exclude(pk=self.pk)
        if name_qs.exists():
            raise ValidationError(
                {"name": "An organization with this name already exists."}
            )

        if self.slug:
            slug_qs = Organization.objects.filter(slug__iexact=self.slug)
            if self.pk:
                slug_qs = slug_qs.exclude(pk=self.pk)
            if slug_qs.exists():
                raise ValidationError(
                    {"slug": "An organization with this slug already exists."}
                )

        if self.registration_number:
            reg_qs = Organization.objects.filter(
                registration_number__iexact=self.registration_number
            )
            if self.pk:
                reg_qs = reg_qs.exclude(pk=self.pk)
            if reg_qs.exists():
                raise ValidationError(
                    {
                        "registration_number": (
                            "An organization with this registration number already exists."
                        )
                    }
                )

        if self.email:
            email_qs = Organization.objects.filter(email__iexact=self.email)
            if self.pk:
                email_qs = email_qs.exclude(pk=self.pk)
            if email_qs.exists():
                raise ValidationError(
                    {"email": "An organization with this email already exists."}
                )

        if self.phone_number:
            phone_qs = Organization.objects.filter(phone_number=self.phone_number)
            if self.pk:
                phone_qs = phone_qs.exclude(pk=self.pk)
            if phone_qs.exists():
                raise ValidationError(
                    {
                        "phone_number": "An organization with this phone number already exists."
                    }
                )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Organization.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Organization member model.
class OrganizationMember(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="organization_members"
    )
    member = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_organizations"
    )
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "organization_members"
        unique_together = ("organization", "member")
        ordering = ["-joined_at"]
        verbose_name = "Organization Member"
        verbose_name_plural = "Organization Members"

    def clean(self):
        super().clean()
        member_qs = OrganizationMember.objects.filter(
            organization=self.organization, member=self.member
        )
        if self.pk:
            member_qs = member_qs.exclude(pk=self.pk)
        if member_qs.exists():
            raise ValidationError(
                {"member": "This user is already a member of the organization."}
            )

    def __str__(self):
        return f"{self.member.phone_number} - {self.organization.name}"


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
        return (
            f"{self.organization.name if self.organization else 'No Organization'} - "
            f"{self.subscription_plan.name if self.subscription_plan else 'No Subscription'}"
        )

    @property
    def is_expired(self):
        return timezone.now().date() > self.end_date

    @classmethod
    def create_free_trial(cls, organization):
        trial_plan = SubscriptionPlan.objects.filter(billing_cycle="FREE_TRIAL").first()
        start_date = timezone.now().date()
        trial_days = (
            trial_plan.trial_days if trial_plan and trial_plan.trial_days else 10
        )
        end_date = start_date + timedelta(days=trial_days)

        return cls.objects.create(
            organization=organization,
            subscription_plan=trial_plan,
            start_date=start_date,
            end_date=end_date,
            status=SubscriptionStatus.TRIAL,
            is_trial=True,
            amount_paid=0,
        )

    @classmethod
    def enforce_for_organization(cls, organization):
        if not organization:
            return True

        latest_subscription = (
            cls.objects.filter(organization=organization)
            .order_by("-created_at")
            .first()
        )
        if not latest_subscription:
            return True

        if latest_subscription.is_trial and latest_subscription.is_expired:
            updates = []
            if latest_subscription.status != SubscriptionStatus.INACTIVE:
                latest_subscription.status = SubscriptionStatus.INACTIVE
                updates.append("status")
            if updates:
                latest_subscription.save(update_fields=updates)

            if organization.is_active:
                organization.is_active = False
                organization.save(update_fields=["is_active"])

            CustomUser.objects.filter(
                organization=organization,
                is_active=True,
            ).update(is_active=False)

            return False

        return True
