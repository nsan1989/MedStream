from django.contrib import admin
from .models import Layout, LayoutZone
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Layout resources.
class LayoutResource(resources.ModelResource):
    class Meta:
        model = Layout
        fields = (
            "id",
            "name",
            "layout_type",
            "resoluttion_width",
            "resoluttion_height",
            "background_color",
            "layout_config",
            "created_by",
            "updated_by",
            "is_active",
        )


# Layout admin.
@admin.register(Layout)
class LayoutAdmin(ImportExportModelAdmin):
    resource_class = LayoutResource
    list_display = (
        "name",
        "layout_type",
        "resoluttion_width",
        "resoluttion_height",
        "is_active",
    )
    search_fields = ("name", "layout_type")
    list_filter = ("layout_type", "is_active")
    ordering = ("-created_at",)


# Layout zone resources.
class LayoutZoneResource(resources.ModelResource):
    class Meta:
        model = LayoutZone
        fields = (
            "id",
            "layout",
            "name",
            "zone_type",
            "position_x",
            "position_y",
            "width",
            "height",
            "z_index",
            "config",
        )


# Layout zone admin.
@admin.register(LayoutZone)
class LayoutZoneAdmin(ImportExportModelAdmin):
    resource_class = LayoutZoneResource
    list_display = (
        "layout",
        "name",
        "zone_type",
        "position_x",
        "position_y",
        "width",
        "height",
        "z_index",
    )
    search_fields = ("name", "zone_type")
    list_filter = ("zone_type",)
    ordering = ("-created_at",)
