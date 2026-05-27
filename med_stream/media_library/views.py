from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import MediaAsset
from .forms import MediaAssetForm
from audit_logs.models import AuditLog


# Media list view.
@login_required
def MediaList(request):

    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    media_list = MediaAsset.objects.none()

    if user.role == "ADMIN":
        media_list = (
            MediaAsset.objects.filter(
                organization=user.organization,
            )
            .select_related(
                "organization",
                "facility",
                "uploaded_by",
            )
            .order_by("-created_at")
        )
    elif user.role == "STAFF":
        media_list = (
            MediaAsset.objects.filter(
                organization=user.organization, facility=user.facility
            )
            .select_related(
                "organization",
                "facility",
                "uploaded_by",
            )
            .order_by("-created_at")
        )

    context = {"media": media_list}

    return render(request, "medias/media_list.html", context)


# Add media view.
@login_required
def AddMedia(request):
    user = request.user

    if user.role not in [
        "ADMIN",
        "STAFF",
    ]:
        raise PermissionDenied

    if request.method == "POST":
        form = MediaAssetForm(request.POST, request.FILES, user=user)

        if form.is_valid():
            media_asset = form.save()
            AuditLog.objects.create(
                organization=user.organization,
                user=user,
                action="MEDIA_UPLOADED",
                target_model="MediaAsset",
                target_id=str(media_asset.id),
                after_data={
                    "title": media_asset.title,
                    "media_type": media_asset.media_type,
                    "facility_id": (
                        str(media_asset.facility_id)
                        if media_asset.facility_id
                        else None
                    ),
                    "uploaded_by_id": (
                        str(media_asset.uploaded_by_id)
                        if media_asset.uploaded_by_id
                        else None
                    ),
                },
                ip_address=request.META.get("REMOTE_ADDR"),
            )
            messages.success(request, "Media asset added successfully.")
            return redirect("media_list")
    else:
        form = MediaAssetForm(user=user)

    context = {
        "form": form,
    }

    return render(request, "medias/add_media.html", context)
