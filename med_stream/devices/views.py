from django.shortcuts import render, redirect
from .forms import DeviceForm
from django.core.exceptions import PermissionDenied
from accounts.enums import UserRole
from facilities.models import Block, Floor
from django.http import JsonResponse
from .models import Device


# Add device form.
def AddDevice(request):

    user = request.user

    if user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise PermissionDenied("You are not allowed to add facilities.")

    if request.method == "POST":
        form = DeviceForm(request.POST, user=user)

        if form.is_valid():
            form.save()

            if user.role == "ADMIN":
                return redirect()
            elif user.role == "STAFF":
                return redirect()

    else:
        form = DeviceForm(user=user)

    context = {"form": form}
    return render(request, "device/add_device.html", context)


# Device list view.
def DeviceListView(request):
    user = request.user

    if user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise PermissionDenied("You are not allowed to view this page.")

    if user.role == UserRole.ADMIN:
        devices = (
            Device.objects.filter(
                facility__organization=user.organization, is_active=True
            )
            .select_related(
                "facility",
                "block",
                "floor",
                "health",
            )
            .order_by("name")
        )
    elif user.role == UserRole.STAFF:
        devices = (
            Device.objects.filter(facility=user.facility, is_active=True)
            .select_related(
                "facility",
                "block",
                "floor",
                "health",
            )
            .order_by("name")
        )

    context = {
        "devices": devices,
    }

    return render(request, "device/device_list.html", context)


# Load blocks.
def load_blocks(request):
    facility_id = request.GET.get("facility_id")

    blocks = Block.objects.filter(facility_id=facility_id)

    data = [
        {
            "id": str(block.id),
            "name": block.name,
        }
        for block in blocks
    ]

    return JsonResponse(
        data,
        safe=False,
    )


# Load floors.
def load_floors(request):
    block_id = request.GET.get("block_id")

    floors = Floor.objects.filter(block_id=block_id)

    data = [
        {
            "id": str(floor.id),
            "name": floor.name,
        }
        for floor in floors
    ]

    return JsonResponse(
        data,
        safe=False,
    )
