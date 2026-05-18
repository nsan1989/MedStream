from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Department, Doctor, OPDRoom, OPDSchedule, DoctorSchedule


class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Department
        fields = ("id", "organization", "name", "created_at", "updated_at")


@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    list_display = ("name", "organization", "created_at")
    list_filter = ("organization", "created_at")
    search_fields = ("name", "organization__name")
    ordering = ("name",)


class DoctorResource(resources.ModelResource):
    class Meta:
        model = Doctor
        fields = (
            "id",
            "organization",
            "facility",
            "department",
            "name",
            "qualification",
            "experience",
            "is_active",
            "created_at",
            "updated_at",
        )


@admin.register(Doctor)
class DoctorAdmin(ImportExportModelAdmin):
    resource_class = DoctorResource
    list_display = (
        "name",
        "organization",
        "facility",
        "department",
        "is_active",
        "created_at",
    )
    list_filter = ("organization", "facility", "department", "is_active", "created_at")
    search_fields = ("name", "organization__name", "facility__name", "department__name")
    ordering = ("name",)
    list_select_related = ("organization", "facility", "department")


class OPDRoomResource(resources.ModelResource):
    class Meta:
        model = OPDRoom
        fields = (
            "id",
            "name",
            "organization",
            "facility",
            "is_active",
            "created_at",
            "updated_at",
        )


@admin.register(OPDRoom)
class OPDRoomAdmin(ImportExportModelAdmin):
    resource_class = OPDRoomResource
    list_display = ("name", "organization", "facility", "is_active", "created_at")
    list_filter = ("organization", "facility", "is_active", "created_at")
    search_fields = ("name", "organization__name", "facility__name")
    ordering = ("name",)
    list_select_related = ("organization", "facility")


class OPDScheduleResource(resources.ModelResource):
    class Meta:
        model = OPDSchedule
        fields = (
            "id",
            "doctor",
            "opd_room",
            "day_of_week",
            "start_time",
            "end_time",
            "is_available",
            "created_at",
            "updated_at",
        )


@admin.register(OPDSchedule)
class OPDScheduleAdmin(ImportExportModelAdmin):
    resource_class = OPDScheduleResource
    list_display = (
        "doctor",
        "opd_room",
        "day_of_week",
        "start_time",
        "end_time",
        "is_available",
    )
    list_filter = ("day_of_week", "is_available", "created_at")
    search_fields = ("doctor__name", "opd_room__name")
    ordering = ("day_of_week", "start_time")
    list_select_related = ("doctor", "opd_room")


class DoctorScheduleResource(resources.ModelResource):
    class Meta:
        model = DoctorSchedule
        fields = (
            "id",
            "doctor",
            "day_of_week",
            "start_time",
            "end_time",
            "is_available",
            "created_at",
            "updated_at",
        )


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(ImportExportModelAdmin):
    resource_class = DoctorScheduleResource
    list_display = (
        "doctor",
        "day_of_week",
        "start_time",
        "end_time",
        "is_available",
    )
    list_filter = ("day_of_week", "is_available", "created_at")
    search_fields = ("doctor__name",)
    ordering = ("day_of_week", "start_time")
    list_select_related = ("doctor",)
