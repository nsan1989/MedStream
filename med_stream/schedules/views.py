from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DepartmentForm, DoctorForm
from .models import Department
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse


# Add department view.
@login_required
def AddDepartment(request):

    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    if request.method == "POST":
        form = DepartmentForm(request.POST, user=user)

        if form.is_valid():
            form.save()

            if user.role == "ADMIN":
                return redirect("admin_dashboard")
            else:
                return redirect("staff_dashboard")

    else:
        form = DepartmentForm(user=user)

    context = {"form": form}

    return render(request, "schedule/add_department.html", context)


# Add doctor view.
@login_required
def AddDoctor(request):

    user = request.user
    departments = Department.objects.none()

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    if request.method == "POST":

        facility_id = request.POST.get("facility")

        if facility_id:
            departments = Department.objects.filter(organization=user.organization)

        form = DoctorForm(request.POST, user=user)

        if "submit_doctor" in request.POST:
            if form.is_valid():
                form.save()

                if user.role == "ADMIN":
                    return redirect("admin_dashboard")

                return redirect("staff_dashboard")

    else:
        form = DoctorForm(user=user)

    context = {
        "form": form,
        "departments": departments,
    }

    return render(request, "schedule/add_doctor.html", context)


# load departments.
@login_required
def load_departments(request):
    organization_id = request.GET.get("organization_id")

    departments = Department.objects.filter(organization_id=organization_id)

    department_data = [
        {"id": str(department.id), "name": department.name}
        for department in departments
    ]

    return JsonResponse({"departments": department_data})
