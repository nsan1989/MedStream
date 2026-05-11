from django.contrib import admin
from .models import Emergency
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# emergency resources.
class EmergencyResource(resources.ModelResource):
    class Meta:
        model = Emergency
        fields = (
            "id",
            "title",
            "message",
            "alert_level",
            "background_color",
            "text_color",
            "is_active",
            "starts_at",
            "ends_at",
            "created_by__phone_number",
        )


# emergency admin.
@admin.register(Emergency)
class EmergencyAdmin(ImportExportModelAdmin):
    resource_class = EmergencyResource
    list_display = (
        "id",
        "title",
        "alert_level",
        "is_active",
        "starts_at",
        "ends_at",
        "created_by",
    )
    list_filter = ("alert_level", "is_active", "starts_at", "ends_at")
    search_fields = ("title", "message", "created_by__phone_number")
