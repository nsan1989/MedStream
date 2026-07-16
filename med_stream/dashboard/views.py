from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils import timezone


from organizations.models import Organization
from facilities.models import Facility
from devices.models import Device, DeviceHealth
from devices.enums import DeviceStatus
from schedules.models import Doctor, OPDSchedule, DoctorSchedule
from broadcasting.models import BroadcastSession
from media_library.models import MediaAsset
from playlists.models import Playlist
import time


# Super admin dashboard view.
@login_required
@never_cache
def SuperAdminDashboard(request):
    all_org = Organization.objects.filter(is_active=True).order_by("created_at")
    total_org = all_org.count()
    all_fac = Facility.objects.filter(is_active=True).order_by("created_at")
    total_fac = all_fac.count()
    context = {
        "org": total_org,
        "fac": total_fac,
    }
    return render(request, "dashboard/super_admin_dashboard.html", context)


# Admin dashboard view.
@login_required
@never_cache
def AdminDashboard(request):
    user = request.user
    today = timezone.localdate()
    current_day = today.weekday()

    context = {
        "total_facilities": Facility.objects.filter(
            organization=user.organization, is_active=True
        ).count(),
        "total_devices": Device.objects.filter(
            facility__organization=user.organization, is_active=True
        ).count(),
        "total_doctors": Doctor.objects.filter(
            organization=user.organization, is_active=True
        ).count(),
        "online_devices": DeviceHealth.objects.filter(
            device__facility__organization=user.organization,
            status=DeviceStatus.ONLINE,
        ).count(),
        "today_opd_count": OPDSchedule.objects.filter(
            doctor__organization=user.organization,
            day_of_week=current_day,
            is_available=True,
        ).count(),
        "out_of_station_today": DoctorSchedule.objects.filter(
            doctor__organization=user.organization,
            doctor__is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).count(),
        "active_broadcasts": BroadcastSession.objects.filter(
            organization=user.organization,
            ended_at__isnull=True,
        ).count(),
        "media_assets": MediaAsset.objects.filter(
            organization=user.organization, is_active=True
        ).count(),
        "playlists": Playlist.objects.filter(
            organization=user.organization, is_active=True
        ).count(),
    }
    return render(request, "dashboard/admin_dashboard.html", context)


# Staff dashboard view.
@login_required
@never_cache
def StaffDashboard(request):
    user = request.user
    today = timezone.localdate()
    current_day = today.weekday()

    context = {
        "total_device": Device.objects.filter(
            facility=user.facility, is_active=True
        ).count(),
        "total_doctors": Doctor.objects.filter(
            facility=user.facility, is_active=True
        ).count(),
        "online_devices": DeviceHealth.objects.filter(
            device__facility=user.facility,
            status=DeviceStatus.ONLINE,
        ).count(),
        "today_opd_count": OPDSchedule.objects.filter(
            doctor__facility=user.facility,
            day_of_week=current_day,
            is_available=True,
        ).count(),
        "out_of_station_today": DoctorSchedule.objects.filter(
            doctor__facility=user.facility,
            doctor__is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).count(),
        "active_broadcasts": BroadcastSession.objects.filter(
            facility=user.facility,
            ended_at__isnull=True,
        ).count(),
        "media_assets": MediaAsset.objects.filter(
            facility=user.facility,
            is_active=True,
        ).count(),
        "playlists": Playlist.objects.filter(
            facility=user.facility,
            is_active=True,
        ).count(),
    }
    return render(request, "dashboard/staff_dashboard.html", context)
