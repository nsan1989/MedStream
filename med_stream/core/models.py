from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


# Base model.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Department model.
class Department(TimeStampedModel):
    name = models.CharField(max_length=255)

    def clean(self):
        super().clean()

        dept_qs = Department.objects.filter(name__iexact=self.name)
        if self.pk:
            dept_qs = dept_qs.exclude(pk=self.pk)
        if dept_qs.exists():
            raise ValidationError(
                {"name": "A department with this name already exists."}
            )

    def __str__(self):
        return self.name


# OTP model.
class PhoneOTP(TimeStampedModel):
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    is_varified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.expires_at
