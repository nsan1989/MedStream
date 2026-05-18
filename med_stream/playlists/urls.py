from django.urls import path
from .views import (
    PlaylistListView,
    AddPlaylistView,
    PlaylistItemListView,
    AddPlaylistItemView,
)

urlpatterns = [
    path("all_playlist/", PlaylistListView, name="playlists"),
    path("all_playlist/add/", AddPlaylistView, name="add_playlist"),
    path(
        "all_playlist/<int:playlist_id>/items/",
        PlaylistItemListView,
        name="playlist_items",
    ),
    path(
        "all_playlist/<int:playlist_id>/items/add/",
        AddPlaylistItemView,
        name="add_playlist_item",
    ),
    path(
        "all_playlist/items/add/", AddPlaylistItemView, name="add_playlist_item_generic"
    ),
]
