from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import BroadcastSession
from .forms import DevicePlaybackForm
from devices.models import DeviceLog
from devices.enums import LogType
from playlists.models import PlaylistItem
from django.utils import timezone


# Broadcast view.
@login_required
def BroadcastView(request):
    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    broadcasts = BroadcastSession.objects.none()
    playback_form = DevicePlaybackForm(user=user)

    if request.method == "POST":
        playback_form = DevicePlaybackForm(request.POST, user=user)
        if playback_form.is_valid():
            device = playback_form.cleaned_data["device"]
            media_asset = playback_form.cleaned_data["media_asset"]
            playlist = playback_form.cleaned_data["playlist"]

            if user.role == "STAFF" and device.facility_id != user.facility_id:
                raise PermissionDenied

            payload = {
                "command": "PLAY",
                "issued_at": timezone.now().isoformat(),
                "organization_id": (
                    str(user.organization_id) if user.organization_id else None
                ),
                "facility_id": str(device.facility_id) if device.facility_id else None,
            }

            if media_asset:
                payload.update(
                    {
                        "source_type": "MEDIA_ASSET",
                        "media_asset_id": str(media_asset.id),
                        "title": media_asset.title,
                        "media_type": media_asset.media_type,
                        "file_url": media_asset.file.url if media_asset.file else "",
                        "thumbnail_url": (
                            media_asset.thumbnail.url if media_asset.thumbnail else ""
                        ),
                    }
                )
            else:
                items = list(
                    PlaylistItem.objects.filter(playlist=playlist)
                    .select_related("media_asset")
                    .order_by("order")
                )
                payload.update(
                    {
                        "source_type": "PLAYLIST",
                        "playlist_id": str(playlist.id),
                        "playlist_name": playlist.name,
                        "items": [
                            {
                                "order": item.order,
                                "duration": item.duration,
                                "media_asset_id": str(item.media_asset.id),
                                "title": item.media_asset.title,
                                "media_type": item.media_asset.media_type,
                                "file_url": (
                                    item.media_asset.file.url
                                    if item.media_asset.file
                                    else ""
                                ),
                            }
                            for item in items
                        ],
                    }
                )

            DeviceLog.objects.create(
                device=device,
                log_type=LogType.INFO,
                message="Playback command issued",
                metadata=payload,
            )
            messages.success(request, f"Play command sent to device {device.name}.")
            return redirect("broadcasts")

    if user.role == "ADMIN":
        broadcasts = (
            BroadcastSession.objects.filter(
                organization=user.organization,
            )
            .select_related(
                "organization",
                "facility",
                "device",
                "doctor_schedule",
                "doctor_schedule__doctor",
                "opdschedule",
                "opdschedule__opd_room",
                "layout",
            )
            .order_by("-started_at")
        )
    elif user.role == "STAFF":
        broadcasts = (
            BroadcastSession.objects.filter(
                organization=user.organization,
                facility=user.facility,
            )
            .select_related(
                "organization",
                "facility",
                "device",
                "doctor_schedule",
                "doctor_schedule__doctor",
                "opdschedule",
                "opdschedule__opd_room",
                "layout",
            )
            .order_by("-started_at")
        )

    context = {
        "broadcasts": broadcasts,
        "playback_form": playback_form,
    }

    return render(request, "broadcast/broadcasts.html", context)
