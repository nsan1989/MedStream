from django.db import models


# Role enums.
class UserRole(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
    ADMIN = "ADMIN", "Admin"
    STAFF = "STAFF", "Staff"
