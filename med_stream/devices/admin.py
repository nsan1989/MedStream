from django.contrib import admin
from .models import Device, DeviceLog, DeviceHealth
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Device resources.
class DeviceResource(resources.ModelResource):
    class Meta:
        model = Device
        fields = (
            "id",
            "name",
            "floor",
            "device_type",
            "orientation",
            "resolution_width",
            "resolution_height",
            "ip_address",
            "is_active",
        )


# Device admin.
@admin.register(Device)
class DeviceAdmin(ImportExportModelAdmin):
    resource_class = DeviceResource
    list_display = (
        "name",
        "device_type",
        "orientation",
        "resolution_width",
        "resolution_height",
        "ip_address",
        "is_active",
    )
    list_filter = ("device_type", "orientation", "is_active")
    search_fields = ("name", "ip_address")


# Device log resources.
class DeviceLogResource(resources.ModelResource):
    class Meta:
        model = DeviceLog
        fields = ("id", "device", "log_type", "message", "metadata")


# Device log admin.
@admin.register(DeviceLog)
class DeviceLogAdmin(ImportExportModelAdmin):
    resource_class = DeviceLogResource
    list_display = ("device", "log_type", "message", "created_at")
    list_filter = ("log_type", "created_at")
    search_fields = ("message",)


# Device health resources.
class DeviceHealthResources(resources.ModelResource):
    class Meta:
        model = DeviceHealth
        fields = (
            "id",
            "device",
            "status",
            "last_seen_at",
            "cpu_usage",
            "memory_usage",
            "disk_usage",
        )


# Device health admin.
@admin.register(DeviceHealth)
class DeviceHealthAdmin(ImportExportModelAdmin):
    resource_class = DeviceHealthResources
    list_display = ("device", "status", "last_seen_at")
    list_filter = ("status", "last_seen_at")
    search_fields = ("device__name",)
