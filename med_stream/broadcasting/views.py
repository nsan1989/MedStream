from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from .models import BroadcastSession
from .forms import DevicePlaybackForm
from devices.models import DeviceLog, Device
from devices.enums import LogType
from layouts.models import Layout
from playlists.models import PlaylistItem
from schedules.models import Doctor, DoctorSchedule, OPDSchedule
from django.utils import timezone
from .enums import BroadcastStatus
from audit_logs.models import AuditLog


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


def _create_broadcast_audit_log(request, user, session, source_type):
    AuditLog.objects.create(
        organization=user.organization,
        user=user,
        action="BROADCAST_SESSION_INITIATED",
        target_model="BroadcastSession",
        target_id=str(session.id),
        after_data={
            "device_id": str(session.device_id) if session.device_id else None,
            "facility_id": str(session.facility_id) if session.facility_id else None,
            "source_type": source_type,
        },
        ip_address=request.META.get("REMOTE_ADDR"),
    )


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
        playback_form = DevicePlaybackForm(
            request.POST,
            user=user,
        )

        if playback_form.is_valid():
            devices = playback_form.cleaned_data["device"]
            media_asset = playback_form.cleaned_data["media_asset"]
            playlist = playback_form.cleaned_data["playlist"]
            doctor_schedule = playback_form.cleaned_data.get("doctor_schedule")
            play_today_opd = playback_form.cleaned_data.get("play_today_opd")

            # STAFF permission check
            if user.role == "STAFF":
                for device in devices:
                    if device.facility != user.facility:
                        raise PermissionDenied

            for device in devices:
                payload = {
                    "command": "PLAY",
                    "issued_at": timezone.now().isoformat(),
                    "organization_id": (
                        str(user.organization_id) if user.organization_id else None
                    ),
                    "facility_id": (
                        str(device.facility_id) if device.facility_id else None
                    ),
                }

                # MEDIA ASSET
                if media_asset:
                    payload.update(
                        {
                            "source_type": "MEDIA_ASSET",
                            "media_asset_id": str(media_asset.id),
                            "title": media_asset.title,
                            "media_type": (media_asset.media_type),
                            "file_url": (
                                media_asset.file.url if media_asset.file else ""
                            ),
                            "thumbnail_url": (
                                media_asset.thumbnail.url
                                if media_asset.thumbnail
                                else ""
                            ),
                        }
                    )
                    try:
                        session = BroadcastSession.objects.create(
                            device=device,
                            media=media_asset,
                            layout=None,
                            started_at=timezone.now(),
                            organization=user.organization,
                            facility=device.facility,
                        )
                        _create_broadcast_audit_log(
                            request=request,
                            user=user,
                            session=session,
                            source_type="MEDIA_ASSET",
                        )

                    except ValidationError as exc:
                        playback_form.add_error(
                            None,
                            (exc.messages if exc.messages else str(exc)),
                        )

                # PLAYLIST
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
                                    "title": (item.media_asset.title),
                                    "media_type": (item.media_asset.media_type),
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
                    layout = _get_broadcast_layout(
                        device,
                        user.organization,
                    )

                    if not layout:
                        playback_form.add_error(
                            None,
                            (
                                "Unable to save broadcast "
                                "session because no active "
                                "layout was found for this "
                                "organization."
                            ),
                        )
                        continue

                    # DOCTOR OUT OF STATION
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
                            .order_by(
                                "doctor__name",
                                "start_date",
                            )
                        )

                        doctor_schedule_items = []

                        for sched in all_doctor_schedules:
                            doctor_schedule_items.append(
                                {
                                    "Doctor": (sched.doctor.name),
                                    "Status": ("Out of Station"),
                                    "From": (sched.start_date.isoformat()),
                                    "To": (sched.end_date.isoformat()),
                                    "Reason": (sched.reason or "-"),
                                }
                            )

                        payload.update(
                            {
                                "source_type": ("DOCTOR_SCHEDULE"),
                                "doctor_schedule_id": str(doctor_schedule.id),
                                "all_doctor_schedules": (doctor_schedule_items),
                            }
                        )

                        try:
                            session = BroadcastSession.objects.create(
                                device=device,
                                doctor_schedule=doctor_schedule,
                                layout=layout,
                                started_at=timezone.now(),
                                organization=user.organization,
                                facility=device.facility,
                            )
                            _create_broadcast_audit_log(
                                request=request,
                                user=user,
                                session=session,
                                source_type="DOCTOR_SCHEDULE",
                            )
                        except ValidationError as exc:
                            playback_form.add_error(
                                None,
                                exc.messages if exc.messages else str(exc),
                            )

                    # MULTIPLE OPD SCHEDULES
                    elif play_today_opd:
                        today = timezone.now().date()
                        current_day = today.weekday()

                        out_of_station_doctor_ids = DoctorSchedule.objects.filter(
                            doctor__organization=user.organization,
                            start_date__lte=today,
                            end_date__gte=today,
                            doctor__is_active=True,
                        ).values_list(
                            "doctor_id",
                            flat=True,
                        )

                        opd_schedules = (
                            OPDSchedule.objects.filter(
                                doctor__organization=user.organization,
                                is_available=True,
                            )
                            .filter(
                                Q(opd_date=today)
                                | Q(
                                    opd_date__isnull=True,
                                    day_of_week=current_day,
                                )
                            )
                            .exclude(doctor_id__in=out_of_station_doctor_ids)
                            .select_related(
                                "doctor",
                                "opd_room",
                            )
                            .order_by(
                                "opd_room__name",
                                "start_time",
                            )
                        )

                        if user.role == "STAFF":
                            opd_schedules = opd_schedules.filter(
                                opd_room__facility=user.facility
                            )

                        opd_schedules = list(opd_schedules)

                        if not opd_schedules:
                            playback_form.add_error(
                                None,
                                (
                                    "No OPD schedules found for today "
                                    "after applying availability and "
                                    "out-of-station filters."
                                ),
                            )
                            continue

                        payload.update(
                            {
                                "source_type": ("OPD_SCHEDULE"),
                                "opd_schedules": [
                                    {
                                        "doctor": (sched.doctor.name),
                                        "opd_room": (sched.opd_room.name),
                                        "department": (
                                            sched.doctor.department.name
                                            if getattr(
                                                sched.doctor,
                                                "department",
                                                None,
                                            )
                                            else "-"
                                        ),
                                        "opd_date": (
                                            sched.opd_date.isoformat()
                                            if sched.opd_date
                                            else ""
                                        ),
                                        "day": (sched.get_day_of_week_display()),
                                        "start_time": (sched.start_time.isoformat()),
                                        "end_time": (sched.end_time.isoformat()),
                                    }
                                    for sched in opd_schedules
                                ],
                            }
                        )

                        try:
                            for sched in opd_schedules:
                                session = BroadcastSession.objects.create(
                                    device=device,
                                    opdschedule=sched,
                                    layout=layout,
                                    started_at=timezone.now(),
                                    organization=user.organization,
                                    facility=device.facility,
                                )
                                _create_broadcast_audit_log(
                                    request=request,
                                    user=user,
                                    session=session,
                                    source_type="OPD_SCHEDULE",
                                )

                        except ValidationError as exc:
                            playback_form.add_error(
                                None,
                                exc.messages if exc.messages else str(exc),
                            )

                # DEVICE LOG
                DeviceLog.objects.create(
                    device=device,
                    log_type=LogType.INFO,
                    message="Playback command issued",
                    metadata=payload,
                )

            if playback_form.errors:
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

                return render(
                    request,
                    "broadcast/broadcasts.html",
                    context,
                )

            messages.success(
                request,
                f"Play command sent to " f"{devices.count()} " f"device(s).",
            )

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

    return render(
        request,
        "broadcast/broadcasts.html",
        context,
    )


# Stop broadcast view.
@login_required
def StopBroadcastView(
    request,
    device_id,
):
    user = request.user

    device = get_object_or_404(
        Device,
        id=device_id,
    )

    # STAFF restriction
    if user.role == "STAFF" and device.facility != user.facility:
        raise PermissionDenied

    broadcast = (
        BroadcastSession.objects.filter(
            device=device,
            ended_at__isnull=True,
        )
        .order_by("-started_at")
        .first()
    )

    if broadcast:
        broadcast.ended_at = timezone.now()
        broadcast.status = BroadcastStatus.COMPLETED
        broadcast.save(update_fields=["ended_at", "status"])

    payload = {
        "command": "STOP",
        "issued_at": (timezone.now().isoformat()),
    }

    DeviceLog.objects.create(
        device=device,
        log_type=LogType.INFO,
        message=("Stop command issued"),
        metadata=payload,
    )

    messages.success(
        request,
        (f"Stop command sent " f"to {device.name}."),
    )

    return redirect("broadcasts")


# All broadcast view.
@login_required
def AllBroadcastView(request):
    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    broadcasts = BroadcastSession.objects.none()

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
    }
    return render(request, "broadcast/all_broadcast.html", context)
