from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from .models import Playlist, PlaylistItem
from .forms import PlaylistForm, PlaylistItemForm
from django.db import transaction


# Playlist view.
@login_required
def PlaylistListView(request):
    user = request.user

    if user.role not in ["ADMIN", "STAFF"]:
        raise PermissionDenied

    playlists = Playlist.objects.none()
    if user.role == "ADMIN":
        playlists = (
            Playlist.objects.filter(organization=user.organization)
            .select_related("organization", "facility", "created_by")
            .order_by("name")
        )
    elif user.role == "STAFF":
        playlists = (
            Playlist.objects.filter(
                organization=user.organization,
                facility=user.facility,
            )
            .select_related("organization", "facility", "created_by")
            .order_by("name")
        )

    context = {"playlists": playlists}
    return render(request, "playlist/playlist_list.html", context)


# Add playlist view.
@login_required
def AddPlaylistView(request):
    user = request.user

    if user.role not in ["ADMIN", "STAFF"]:
        raise PermissionDenied

    if request.method == "POST":
        form = PlaylistForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Playlist added successfully.")
            return redirect("playlists")
    else:
        form = PlaylistForm(user=user)

    context = {"form": form}
    return render(request, "playlist/add_playlist.html", context)


# Playlist items view.
@login_required
def PlaylistItemListView(request, playlist_id):
    user = request.user

    if user.role not in ["ADMIN", "STAFF"]:
        raise PermissionDenied

    playlist = get_object_or_404(Playlist, id=playlist_id)

    if playlist.organization_id != user.organization_id:
        raise PermissionDenied
    if user.role == "STAFF" and playlist.facility_id != user.facility_id:
        raise PermissionDenied

    playlist_items = (
        PlaylistItem.objects.filter(playlist=playlist)
        .select_related("playlist", "media_asset")
        .order_by("order")
    )

    context = {"playlist": playlist, "playlist_items": playlist_items}
    return render(request, "playlist/playlist_item_list.html", context)


# Add playlist item view.
@login_required
@transaction.atomic
def AddPlaylistItemView(request, playlist_id=None):
    user = request.user

    if user.role not in ["ADMIN", "STAFF"]:
        raise PermissionDenied

    playlist = None

    if playlist_id is not None:
        playlist = get_object_or_404(Playlist, id=playlist_id)

        if playlist.organization_id != user.organization_id:
            raise PermissionDenied

        if user.role == "STAFF" and playlist.facility_id != user.facility_id:
            raise PermissionDenied

    if request.method == "POST":
        form = PlaylistItemForm(
            request.POST,
            user=user,
            playlist=playlist,
        )

        if form.is_valid():
            playlist_obj = form.cleaned_data["playlist"]

            duration = form.cleaned_data.get("duration")

            media_assets = form.cleaned_data.get("media_assets") or []

            opd_schedules = form.cleaned_data.get("opd_schedules") or []

            doctor_schedules = form.cleaned_data.get("doctor_schedules") or []

            # Get next available order
            last_item = (
                PlaylistItem.objects.filter(playlist=playlist_obj)
                .order_by("-order")
                .first()
            )

            current_order = last_item.order + 1 if last_item else 1

            items_to_create = []

            # Create media items
            for media in media_assets:
                items_to_create.append(
                    PlaylistItem(
                        playlist=playlist_obj,
                        media_asset=media,
                        order=current_order,
                        duration=duration,
                    )
                )
                current_order += 1

            # Create OPD schedule items
            for opd in opd_schedules:
                items_to_create.append(
                    PlaylistItem(
                        playlist=playlist_obj,
                        opd_schedule=opd,
                        order=current_order,
                        duration=None,
                    )
                )
                current_order += 1

            # Create doctor schedule items
            for doctor in doctor_schedules:
                items_to_create.append(
                    PlaylistItem(
                        playlist=playlist_obj,
                        doctor_schedule=doctor,
                        order=current_order,
                        duration=None,
                    )
                )
                current_order += 1

            # Save all
            for item in items_to_create:
                item.save()

            messages.success(
                request, f"{len(items_to_create)} playlist item(s) added successfully."
            )

            if playlist is not None:
                return redirect(
                    "playlist_items",
                    playlist_id=playlist.id,
                )

            return redirect("playlists")

    else:
        form = PlaylistItemForm(
            user=user,
            playlist=playlist,
        )

    context = {
        "form": form,
        "playlist": playlist,
    }

    return render(
        request,
        "playlist/add_playlist_item.html",
        context,
    )
