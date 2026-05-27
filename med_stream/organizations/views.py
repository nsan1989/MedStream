from django.shortcuts import render
from .models import OrganizationMember, Organization
from accounts.enums import UserRole
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


# All organization.
@login_required
def AllOrganizationView(request):

    user = request.user

    if user.role not in [UserRole.SUPER_ADMIN]:
        raise PermissionDenied("You are not allowed to view this page.")

    all_org = Organization.objects.all()

    context = {
        "org": all_org,
    }
    return render(request, "organization/all_org.html", context)


# Organization staff.
@login_required
def OrganizationStaff(request):

    user = request.user

    if user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise PermissionDenied("You are not allowed to view this page.")

    org_staff = OrganizationMember.objects.filter(
        organization=user.organization, is_active=True
    ).order_by("-joined_at")

    context = {
        "staff": org_staff,
    }
    return render(request, "organization/org_staff.html", context)
