from django.contrib import admin
from .models import MediaAsset

from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Media asset resources.
class MediaAssetResource(resources.ModelResource):
    class Meta:
        model = MediaAsset
        fields = (
            "id",
            "title",
            "description",
            "media_type",
            "file",
            "thumbnail",
            "duration",
            "tags",
            "uploaded_by",
            "is_active",
            "is_public",
        )


# Media asset admin.
@admin.register(MediaAsset)
class MediaAssetAdmin(ImportExportModelAdmin):
    resource_class = MediaAssetResource
    list_display = ("title", "media_type", "uploaded_by", "is_active", "is_public")
    search_fields = ("title", "description", "tags")
    list_filter = ("media_type", "is_active", "is_public")
