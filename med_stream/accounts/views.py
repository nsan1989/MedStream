from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from .models import CustomUser


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
                if "organization" in request.POST or "role" in request.POST
                else "login"
            )

        if action == "register":
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                organization = register_form.cleaned_data["organization"]
                role = register_form.cleaned_data["role"]

                if role == "ADMIN":
                    admin_exists = CustomUser.objects.filter(
                        organization=organization,
                        role="ADMIN",
                    ).exists()
                    if admin_exists:
                        messages.error(
                            request,
                            "This organization already has an admin. Please register as staff.",
                        )
                        return redirect("register")

                try:
                    register_form.save()
                except IntegrityError:
                    messages.error(
                        request,
                        "A user with these details already exists. Please use different details.",
                    )
                    return redirect("register")

                messages.success(request, "Registration successful. Please log in.")
                return redirect("login")

            messages.error(request, "Please provide valid registration details.")

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
                    return redirect("index")

                messages.error(request, "Invalid credentials.")
            else:
                messages.error(request, "Please provide valid login details.")

    context = {
        "register_form": register_form,
        "login_form": login_form,
    }

    return render(request, "accounts/auth.html", context)
