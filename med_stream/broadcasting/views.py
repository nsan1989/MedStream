from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from .models import BroadcastSession
from .forms import DevicePlaybackForm
from devices.models import DeviceLog
from devices.enums import LogType
from layouts.models import Layout
from playlists.models import PlaylistItem
from schedules.models import Doctor, DoctorSchedule, OPDSchedule
from django.utils import timezone


def _get_broadcast_layout(device, organization):
    layout_qs = Layout.objects.filter(is_active=True)

    if organization:
        layout_qs = layout_qs.filter(organization=organization)

    layout = layout_qs.filter(layout_type=device.orientation).order_by("name").first()
    if layout:
        return layout

    layout = layout_qs.order_by("name").first()
    if layout:
        return layout

    # Fall back to an active global layout if no organization-specific layout exists.
    layout = (
        Layout.objects.filter(organization__isnull=True, is_active=True)
        .order_by("name")
        .first()
    )
    return layout


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
            doctor_schedule = playback_form.cleaned_data.get("doctor_schedule")
            opdschedule = playback_form.cleaned_data.get("opdschedule")

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
            elif playlist:
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
            else:
                layout = _get_broadcast_layout(device, user.organization)
                if not layout:
                    playback_form.add_error(
                        None,
                        "Unable to save broadcast "
                        "session because no active "
                        "layout was found for this "
                        "organization.",
                    )
                elif doctor_schedule:
                    all_doctors = Doctor.objects.filter(
                        organization=user.organization,
                        is_active=True,
                    )
                    if user.role == "STAFF":
                        all_doctors = all_doctors.filter(facility=user.facility)

                    all_doctor_schedules = (
                        DoctorSchedule.objects.filter(
                            doctor__in=all_doctors,
                        )
                        .select_related("doctor")
                        .order_by("doctor__name", "day_of_week", "start_time")
                    )

                    doctor_schedule_items = []
                    for sched in all_doctor_schedules:
                        item = {
                            "Doctor": sched.doctor.name,
                            "Status": (
                                "Out of Station"
                                if (
                                    sched.out_of_station_start_date
                                    and sched.out_of_station_end_date
                                )
                                else (
                                    "Available" if sched.is_available else "Unavailable"
                                )
                            ),
                        }

                        if (
                            sched.out_of_station_start_date
                            and sched.out_of_station_end_date
                        ):
                            item["From"] = sched.out_of_station_start_date.isoformat()
                            item["To"] = sched.out_of_station_end_date.isoformat()
                        else:
                            item["Day"] = (
                                sched.get_day_of_week_display()
                                if sched.day_of_week is not None
                                else "-"
                            )
                            item["Start"] = sched.start_time.isoformat()
                            item["End"] = sched.end_time.isoformat()

                        doctor_schedule_items.append(item)

                    payload.update(
                        {
                            "source_type": "DOCTOR_SCHEDULE",
                            "doctor_schedule_id": str(doctor_schedule.id),
                            "all_doctor_schedules": doctor_schedule_items,
                        }
                    )
                    try:
                        BroadcastSession.objects.create(
                            device=device,
                            doctor_schedule=doctor_schedule,
                            layout=layout,
                            started_at=timezone.now(),
                            organization=user.organization,
                            facility=device.facility,
                        )
                    except ValidationError as exc:
                        playback_form.add_error(
                            None,
                            exc.messages if exc.messages else str(exc),
                        )
                elif opdschedule:
                    payload.update(
                        {
                            "source_type": "OPD_SCHEDULE",
                            "opdschedule_id": str(opdschedule.id),
                            "opd_room_name": opdschedule.opd_room.name,
                            "opd_schedule_day": opdschedule.get_day_of_week_display(),
                            "opd_schedule_start": opdschedule.start_time.isoformat(),
                            "opd_schedule_end": opdschedule.end_time.isoformat(),
                        }
                    )
                    try:
                        BroadcastSession.objects.create(
                            device=device,
                            opdschedule=opdschedule,
                            layout=layout,
                            started_at=timezone.now(),
                            organization=user.organization,
                            facility=device.facility,
                        )
                    except ValidationError as exc:
                        playback_form.add_error(
                            None,
                            exc.messages if exc.messages else str(exc),
                        )

            if playback_form.errors:
                # Render the page again so errors can be displayed without issuing a command.
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
