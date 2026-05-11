from django.db import models
from django.core.exceptions import ValidationError


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
