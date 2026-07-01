from django.db import models


class OrganizationRole(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"


class OrganizationType(models.TextChoices):
    HOSPITAL = "HOSPITAL", "Hospital"
    CLINIC = "CLINIC", "Clinic"
    PHARMACY = "PHARMACY", "Pharmacy"
    LABORATORY = "LABORATORY", "Laboratory"
    OTHER = "OTHER", "Other"


class SubscriptionStatus(models.TextChoices):
    TRIAL = "TRIAL", "Trial"
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    PENDING = "PENDING", "Pending"
    CANCELLED = "CANCELLED", "Cancelled"
