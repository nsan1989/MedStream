from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


from organizations.models import Organization
from facilities.models import Facility


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
    context = {}
    return render(request, "dashboard/admin_dashboard.html", context)


# Staff dashboard view.
@login_required
@never_cache
def StaffDashboard(request):
    context = {}
    return render(request, "dashboard/staff_dashboard.html", context)
