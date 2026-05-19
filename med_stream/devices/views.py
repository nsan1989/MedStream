from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DeviceForm
from django.core.exceptions import PermissionDenied
from accounts.enums import UserRole
from facilities.models import Block, Floor
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import get_object_or_404
import json
from .models import Device
from .models import DeviceLog
from .enums import LogType


# Add device form.
@login_required
def AddDevice(request):

    user = request.user

    if user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise PermissionDenied("You are not allowed to add facilities.")

    if request.method == "POST":
        form = DeviceForm(request.POST, user=user)

        if form.is_valid():
            form.save()

            if user.role == "ADMIN":
                return redirect("devices")
            elif user.role == "STAFF":
                return redirect("devices")

    else:
        form = DeviceForm(user=user)

    context = {"form": form}
    return render(request, "device/add_device.html", context)


# Device list view.
@login_required
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
@login_required
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
@login_required
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


# Device player: pull latest play command.
@require_GET
def DeviceNextCommand(request, device_id):
    device = get_object_or_404(Device, id=device_id, is_active=True)

    # Optional simple check: caller IP should match the registered device IP.
    remote_ip = request.META.get("REMOTE_ADDR")
    if (
        remote_ip
        and remote_ip not in ["127.0.0.1", "::1"]
        and remote_ip != device.ip_address
    ):
        return JsonResponse({"detail": "IP mismatch for device."}, status=403)

    logs = DeviceLog.objects.filter(device=device, log_type=LogType.INFO).order_by(
        "-created_at"
    )[:50]

    command_log = None
    for log in logs:
        metadata = log.metadata or {}
        if metadata.get("command") == "PLAY" and not metadata.get("executed", False):
            command_log = log
            break

    if not command_log:
        return JsonResponse({"command": None, "detail": "No pending play command."})

    return JsonResponse(
        {
            "command_id": str(command_log.id),
            "device_id": str(device.id),
            "device_name": device.name,
            "payload": command_log.metadata or {},
            "created_at": command_log.created_at.isoformat(),
        }
    )


# Device player: acknowledge command execution.
@csrf_exempt
@require_POST
def DeviceCommandAck(request, device_id):
    device = get_object_or_404(Device, id=device_id, is_active=True)

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    command_id = body.get("command_id")
    status = body.get("status", "ACK")
    message = body.get("message", "")

    DeviceLog.objects.create(
        device=device,
        log_type=LogType.INFO,
        message="Playback command acknowledged",
        metadata={
            "command": "ACK",
            "command_id": command_id,
            "status": status,
            "message": message,
            "ack_at": timezone.now().isoformat(),
        },
    )

    return JsonResponse({"ok": True})


def get_remote_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


# Device-side auto-launch player page.
@require_GET
def DevicePlayerAutoPage(request):
    remote_ip = get_remote_ip(request)
    if not remote_ip:
        return HttpResponse("Unable to determine device IP.", status=400)

    device = Device.objects.filter(ip_address=remote_ip, is_active=True).first()
    if not device:
        return HttpResponse(
            "No active device registered for this IP address.", status=404
        )

    return redirect("device_player_page", device_id=device.id)


# Device-side player page.
@require_GET
def DevicePlayerPage(request, device_id):
    device = get_object_or_404(Device, id=device_id, is_active=True)
    context = {"device": device}
    return render(request, "device/player.html", context)
