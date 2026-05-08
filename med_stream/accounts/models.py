from django.db import models
from .manager import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .enums import UserRole


# User model.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.USER
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number
