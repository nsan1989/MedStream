from django import forms
from .models import CustomUser
from .enums import UserRole
import re
from django.core.exceptions import ValidationError
from django.db import transaction
from organizations.models import (
    Organization,
    OrganizationMember,
    OrganizationSubscription,
)
from organizations.enums import OrganizationType


# Register form.
class RegisterForm(forms.Form):
    organization_name = forms.CharField(max_length=255, required=True)
    organization_type = forms.ChoiceField(
        choices=OrganizationType.choices, required=True
    )
    phone_number = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fieldname in [
            "organization_name",
            "organization_type",
            "phone_number",
            "password",
        ]:
            self.fields[fieldname].help_text = None

    def clean_organization_name(self):
        organization_name = self.cleaned_data.get("organization_name", "").strip()
        if Organization.objects.filter(name__iexact=organization_name).exists():
            raise forms.ValidationError("An organization with this name already exists.")
        return organization_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not re.fullmatch(r"^[A-Za-z0-9@&!]+$", password):
            raise ValidationError(
                "Password can contain only letters, numbers, and '@&!'."
            )

        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.")

        return password

    def save(self):
        with transaction.atomic():
            organization = Organization.objects.create(
                name=self.cleaned_data["organization_name"],
                organization_type=self.cleaned_data["organization_type"],
            )

            user = CustomUser.objects.create_user(
                phone_number=self.cleaned_data["phone_number"],
                password=self.cleaned_data["password"],
                role=UserRole.ADMIN,
                organization=organization,
            )

            OrganizationMember.objects.create(
                organization=organization,
                member=user,
                is_active=True,
            )

            OrganizationSubscription.create_free_trial(organization)

        return user


# Login form.
class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for fieldname in ["phone_number", "password"]:
            self.fields[fieldname].help_text = None
