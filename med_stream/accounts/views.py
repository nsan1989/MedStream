from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


from .forms import RegisterForm, LoginForm, StaffRegisterForm
from accounts.models import CustomUser
from accounts.enums import UserRole
from organizations.models import (
    Organization,
    OrganizationMember,
    OrganizationSubscription,
)

from core.models import PhoneOTP
from core.services.otp_service import generate_otp
from utils.message import send_otp


# Auth view.
def authView(request):
    register_form = RegisterForm()
    staff_form = StaffRegisterForm()
    login_form = LoginForm()

    organizations = Organization.objects.filter(is_active=True)

    if request.method == "POST":
        action = request.POST.get("action")

        # Admin Register.
        if action == "admin_register":
            register_form = RegisterForm(request.POST)

            if register_form.is_valid():

                phone_number = register_form.cleaned_data["phone_number"]

                otp = generate_otp()

                try:
                    send_otp(
                        phone_number,
                        otp,
                    )
                    PhoneOTP.objects.update_or_create(
                        phone_number=phone_number,
                        defaults={
                            "otp": otp,
                        },
                    )
                    request.session["pending_registration"] = {
                        "registration_type": "admin",
                        "organization_name": register_form.cleaned_data[
                            "organization_name"
                        ],
                        "organization_type": register_form.cleaned_data[
                            "organization_type"
                        ],
                        "phone_number": phone_number,
                        "password": register_form.cleaned_data["password"],
                    }

                    messages.success(
                        request,
                        "OTP sent successfully " "to your phone number.",
                    )

                    return redirect("verify_otp")

                except Exception:
                    messages.error(
                        request,
                        "Unable to send OTP. " "Please try again.",
                    )

            messages.error(
                request,
                "Please provide valid admin registration details.",
            )

        # Staff Register.
        elif action == "staff_register":
            staff_form = StaffRegisterForm(request.POST)

            if staff_form.is_valid():
                phone_number = staff_form.cleaned_data["phone_number"]

                otp = generate_otp()

                try:
                    send_otp(
                        phone_number,
                        otp,
                    )

                    PhoneOTP.objects.update_or_create(
                        phone_number=phone_number,
                        defaults={
                            "otp": otp,
                        },
                    )

                    organization = staff_form.cleaned_data["organization"]

                    request.session["pending_registration"] = {
                        "registration_type": "staff",
                        "organization_id": str(organization.id),
                        "phone_number": phone_number,
                        "password": staff_form.cleaned_data["password"],
                    }

                    messages.success(
                        request,
                        "OTP sent successfully " "to your phone number.",
                    )

                    return redirect("verify_otp")

                except Exception:
                    messages.error(
                        request,
                        "Unable to send OTP. " "Please try again.",
                    )

            messages.error(
                request,
                "Please provide valid staff registration details.",
            )

        # Login.
        elif action == "login":
            login_form = LoginForm(request.POST)

            if login_form.is_valid():
                phone_number = login_form.cleaned_data["phone_number"]
                password = login_form.cleaned_data["password"]

                login_user = authenticate(
                    request,
                    phone_number=phone_number,
                    password=password,
                )

                if login_user is not None:
                    login(request, login_user)

                    messages.success(
                        request,
                        "Login successful.",
                    )

                    if login_user.role == UserRole.SUPER_ADMIN:
                        return redirect("super_admin_dashboard")

                    elif login_user.role == UserRole.ADMIN:
                        return redirect("admin_dashboard")

                    elif login_user.role == UserRole.STAFF:
                        return redirect("staff_dashboard")

                messages.error(
                    request,
                    "Invalid credentials.",
                )

            else:
                messages.error(
                    request,
                    "Please provide valid login details.",
                )

    context = {
        "register_form": register_form,
        "staff_form": staff_form,
        "login_form": login_form,
        "organizations": organizations,
    }

    return render(request, "accounts/auth.html", context)


# Logout view.
def logoutView(request):
    logout(request)

    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


# Verify OTP View
def verifyOTPView(request):
    if request.method != "POST":
        return redirect("register")

    entered_otp = request.POST.get("otp")

    registration_data = request.session.get("pending_registration")

    if not registration_data:
        messages.error(
            request,
            "Registration session expired.",
        )
        return redirect("register")

    phone_number = registration_data["phone_number"]

    try:
        otp_obj = PhoneOTP.objects.get(phone_number=phone_number)

    except PhoneOTP.DoesNotExist:
        messages.error(
            request,
            "OTP not found.",
        )
        return redirect("register")

    # Validate OTP
    if otp_obj.otp != entered_otp:
        messages.error(
            request,
            "Invalid OTP.",
        )
        return redirect("register")

    # ==========================
    # CREATE ACCOUNT
    # ==========================
    registration_type = registration_data["registration_type"]

    try:
        if registration_type == "admin":

            organization = Organization.objects.create(
                name=registration_data["organization_name"],
                organization_type=registration_data["organization_type"],
            )

            user = CustomUser.objects.create_user(
                phone_number=registration_data["phone_number"],
                password=registration_data["password"],
                role=UserRole.ADMIN,
                organization=organization,
            )

            OrganizationMember.objects.create(
                organization=organization,
                member=user,
                is_active=True,
            )

            OrganizationSubscription.create_free_trial(organization)

        elif registration_type == "staff":

            organization = Organization.objects.get(
                id=registration_data["organization_id"]
            )

            user = CustomUser.objects.create_user(
                phone_number=registration_data["phone_number"],
                password=registration_data["password"],
                role=UserRole.STAFF,
                organization=organization,
            )

            OrganizationMember.objects.create(
                organization=organization,
                member=user,
                is_active=True,
            )

        # cleanup
        otp_obj.delete()

        del request.session["pending_registration"]

        messages.success(
            request,
            "Phone verified successfully. " "Please log in.",
        )

        return redirect("login")

    except Exception:
        messages.error(
            request,
            "Unable to complete registration.",
        )

        return redirect("register")


# Resend OTP View
def resendOTPView(request):
    registration_data = request.session.get("pending_registration")

    if not registration_data:
        messages.error(
            request,
            "Session expired.",
        )
        return redirect("register")

    phone_number = registration_data["phone_number"]

    otp = generate_otp()

    PhoneOTP.objects.update_or_create(
        phone_number=phone_number,
        defaults={
            "otp": otp,
        },
    )

    send_otp(phone_number, otp)

    messages.success(
        request,
        "OTP resent successfully.",
    )

    return redirect("register")
