from django import forms
from .models import CustomUser
from .enums import UserRole
import re
from django.core.exceptions import ValidationError


# Register form.
class RegisterForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    role = forms.ChoiceField(choices=UserRole.choices, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fieldname in ["phone_number", "password", "role"]:
            self.fields[fieldname].help_text = None

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

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if role not in [UserRole.ADMIN.value, UserRole.STAFF.value]:
            raise forms.ValidationError("Invalid role selected.")
        return role


# Login form.
class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for fieldname in ["phone_number", "password"]:
            self.fields[fieldname].help_text = None
