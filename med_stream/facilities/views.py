from django.shortcuts import render, redirect
from .forms import BlockForm, FloorForm, FacilityForm, StaffForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


# Add staff view.
@login_required
def AddStaff(request):
    user = request.user

    if user.role != "ADMIN":
        raise PermissionDenied("You are not allowed to add facilities.")

    if request.method == "POST":
        form = StaffForm(request.POST, user=user)

        if form.is_valid():
            facility = form.cleaned_data["facility"]
            staff_members = form.cleaned_data["facility_staff"]
            facility.facility_staff.set(staff_members)

            return redirect("admin_dashboard")

    else:
        form = StaffForm(user=user)

    context = {"form": form}
    return render(request, "facility/add_staff.html", context)


# Add facility view.
@login_required
def AddFacility(request):
    user = request.user

    if user.role != "ADMIN":
        raise PermissionDenied("You are not allowed to add facilities.")

    if request.method == "POST":
        form = FacilityForm(request.POST)

        if form.is_valid():
            facility = form.save(commit=False)

            facility.organization = user.organization

            facility.save()

            return redirect("admin_dashboard")

    else:
        form = FacilityForm()

    context = {"form": form}
    return render(request, "facility/add_facility.html", context)


# Add block view.
@login_required
def AddBlock(request):
    user = request.user

    if user.role not in ["ADMIN", "STAFF"]:
        raise PermissionDenied

    if request.method == "POST":
        form = BlockForm(request.POST, user=user)

        if form.is_valid():
            form.save()

            if user.role == "ADMIN":
                return redirect("admin_dashboard")
            else:
                return redirect("staff_dashboard")

    else:
        form = BlockForm(user=user)

    context = {
        "form": form,
    }

    return render(request, "facility/add_block.html", context)


# Add floor view.
@login_required
def AddFloor(request):
    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    if request.method == "POST":
        form = FloorForm(request.POST, user=user)

        if form.is_valid():
            form.save()

            if user.role == "ADMIN":
                return redirect("admin_dashboard")
            else:
                return redirect("staff_dashboard")

    else:
        form = FloorForm(user=user)

    context = {
        "form": form,
    }

    return render(request, "facility/add_floor.html", context)
