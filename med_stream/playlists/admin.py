from django.contrib import admin
from .models import Playlist, PlaylistItem
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Playlist resources.
class PlaylistResource(resources.ModelResource):
    class Meta:
        model = Playlist
        fields = (
            "id",
            "name",
            "organization__name",
            "facility__name",
            "description",
            "created_by__phone_number",
            "is_active",
        )
        export_order = (
            "id",
            "name",
            "organization__name",
            "facility__name",
            "description",
            "created_by__phone_number",
            "is_active",
        )


# Playlist admin.
@admin.register(Playlist)
class PlaylistAdmin(ImportExportModelAdmin):
    resource_class = PlaylistResource
    list_display = (
        "id",
        "name",
        "organization",
        "facility",
        "created_by",
        "is_active",
        "created_at",
    )
    list_filter = ("organization", "facility", "is_active", "created_at")
    search_fields = (
        "name",
        "description",
        "organization__name",
        "facility__name",
        "created_by__phone_number",
    )


# Playlist item resources.
class PlaylistItemResource(resources.ModelResource):
    class Meta:
        model = PlaylistItem
        fields = ("id", "playlist__name", "media_asset__title", "order", "duration")
        export_order = (
            "id",
            "playlist__name",
            "media_asset__title",
            "order",
            "duration",
        )


# Playlist item admin.
@admin.register(PlaylistItem)
class PlaylistItemAdmin(ImportExportModelAdmin):
    resource_class = PlaylistItemResource
    list_display = ("id", "playlist", "media_asset", "order", "duration", "created_at")
    list_filter = ("playlist", "created_at")
    search_fields = ("playlist__name", "media_asset__title")
