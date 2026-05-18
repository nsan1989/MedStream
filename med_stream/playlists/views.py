from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from .models import Playlist, PlaylistItem
from .forms import PlaylistForm, PlaylistItemForm


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
        form = PlaylistItemForm(request.POST, user=user, playlist=playlist)
        if form.is_valid():
            form.save()
            messages.success(request, "Playlist item added successfully.")
            if playlist is not None:
                return redirect("playlist_items", playlist_id=playlist.id)
            return redirect("playlists")
    else:
        form = PlaylistItemForm(user=user, playlist=playlist)

    context = {"form": form, "playlist": playlist}
    return render(request, "playlist/add_playlist_item.html", context)
