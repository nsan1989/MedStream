from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError


from .forms import RegisterForm, LoginForm


# Auth view.
def authView(request):
    register_form = RegisterForm()
    login_form = LoginForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action not in ["register", "login"]:
            action = (
                "register"
                if "organization_name" in request.POST
                or "organization_type" in request.POST
                else "login"
            )

        # Register
        if action == "register":
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                try:
                    register_form.save()
                except IntegrityError:
                    messages.error(
                        request,
                        "Unable to complete registration due to duplicate data.",
                    )
                    return redirect("register")

                messages.success(
                    request,
                    "Organization registered successfully. Trial activated for 10 days. Please log in as admin.",
                )
                return redirect("login")

            messages.error(request, "Please provide valid registration details.")

        # Login
        if action == "login":
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                phone_number = login_form.cleaned_data["phone_number"]
                password = login_form.cleaned_data["password"]
                login_user = authenticate(
                    request, phone_number=phone_number, password=password
                )
                if login_user is not None:
                    login(request, login_user)
                    messages.success(request, "Login successful.")
                    if login_user.role == "SUPER_ADMIN":
                        return redirect("super_admin_dashboard")
                    elif login_user.role == "ADMIN":
                        return redirect("admin_dashboard")
                    else:
                        return redirect("staff_dashboard")

                messages.error(request, "Invalid credentials.")
            else:
                messages.error(request, "Please provide valid login details.")

    context = {
        "register_form": register_form,
        "login_form": login_form,
    }

    return render(request, "accounts/auth.html", context)


# Logout view.
def logoutView(request):
    logout(request)

    messages.success(request, "You have been logged out successfully.")
    return redirect("login")
