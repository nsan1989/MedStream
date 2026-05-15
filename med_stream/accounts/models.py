from django.db import models
from django.core.exceptions import ValidationError
from .manager import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .enums import UserRole


# User model.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    phone_number = models.CharField(max_length=15, unique=True)
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.STAFF
    )
    email = models.EmailField(max_length=255, blank=True, null=True, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = []

    def clean(self):
        super().clean()

        phone_qs = CustomUser.objects.filter(phone_number=self.phone_number)
        if self.pk:
            phone_qs = phone_qs.exclude(pk=self.pk)
        if phone_qs.exists():
            raise ValidationError(
                {"phone_number": "A user with this phone number already exists."}
            )

        if self.email:
            email_qs = CustomUser.objects.filter(email__iexact=self.email)
            if self.pk:
                email_qs = email_qs.exclude(pk=self.pk)
            if email_qs.exists():
                raise ValidationError(
                    {"email": "A user with this email already exists."}
                )

    def __str__(self):
        return self.phone_number
