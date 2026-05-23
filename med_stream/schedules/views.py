from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    DepartmentForm,
    DoctorForm,
    OPDRoomForm,
    OPDScheduleForm,
    DoctorScheduleForm,
)
from .models import (
    Department,
    OPDRoom,
    OPDSchedule,
    DoctorSchedule as DoctorScheduleModel,
)
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils import timezone

today = timezone.now().date()


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


# OPD room.
@login_required
def OpdRoom(request):

    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    if request.method == "POST":
        form = OPDRoomForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "OPD room added successfully.")

            if user.role == "ADMIN":
                return redirect("schedules")
            return redirect("schedules")
    else:
        form = OPDRoomForm(user=user)

    context = {"form": form}

    return render(request, "schedule/add_opd_room.html", context)


# OPD Schedule.
@login_required
def OpdSchedule(request):
    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    if request.method == "POST":
        form = OPDScheduleForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "OPD schedule added successfully.")

            if user.role == "ADMIN":
                return redirect("schedules")
            return redirect("schedules")
    else:
        form = OPDScheduleForm(user=user)

    context = {"form": form}

    return render(request, "schedule/add_opd_schedule.html", context)


# Doctor Schedule.
@login_required
def DoctorSchedule(request):
    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    if request.method == "POST":
        form = DoctorScheduleForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor schedule added successfully.")

            if user.role == "ADMIN":
                return redirect("schedules")
            return redirect("schedules")
    else:
        form = DoctorScheduleForm(user=user)

    context = {"form": form}

    return render(request, "schedule/add_doctor_schedule.html", context)


# Schedules view.
@login_required
def SchedulesView(request):
    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    opd_rooms = OPDRoom.objects.none()
    opd_schedules = OPDSchedule.objects.none()
    doctor_schedules = DoctorScheduleModel.objects.none()

    if user.role == "ADMIN":
        opd_rooms = (
            OPDRoom.objects.filter(
                organization=user.organization,
                is_active=True,
            )
            .select_related("organization", "facility")
            .order_by("facility__name", "name")
        )
        opd_schedules = (
            OPDSchedule.objects.filter(
                doctor__organization=user.organization,
                opd_room__organization=user.organization,
                day_of_week=today.weekday(),
                is_available=True,
            )
            .select_related(
                "doctor",
                "doctor__facility",
                "opd_room",
            )
            .order_by(
                "start_time",
            )
        )
        doctor_schedules = (
            DoctorScheduleModel.objects.filter(
                doctor__organization=user.organization,
            )
            .select_related(
                "doctor",
                "doctor__facility",
            )
            .order_by(
                "start_date",
            )
        )
    elif user.role == "STAFF":
        opd_rooms = (
            OPDRoom.objects.filter(
                organization=user.organization,
                facility=user.facility,
                is_active=True,
            )
            .select_related("organization", "facility")
            .order_by("name")
        )
        opd_schedules = (
            OPDSchedule.objects.filter(
                doctor__organization=user.organization,
                doctor__facility=user.facility,
                opd_room__facility=user.facility,
                day_of_week=today.weekday(),
                is_available=True,
            )
            .select_related(
                "doctor",
                "doctor__facility",
                "opd_room",
            )
            .order_by(
                "start_time",
            )
        )
        doctor_schedules = (
            DoctorScheduleModel.objects.filter(
                doctor__organization=user.organization,
                doctor__facility=user.facility,
            )
            .select_related(
                "doctor",
                "doctor__facility",
            )
            .order_by(
                "start_date",
            )
        )

    context = {
        "opd_rooms": opd_rooms,
        "opd_schedules": opd_schedules,
        "doctor_schedules": doctor_schedules,
    }

    return render(request, "schedule/schedules.html", context)
