from import_export import resources
from import_export.admin import ImportExportModelAdmin


from django.contrib import admin
from .models import Block, Floor, Facility


# Block resource.
class BlockResource(resources.ModelResource):
    class Meta:
        model = Block
        fields = ("id", "name")


# Block admin.
@admin.register(Block)
class BlockAdmin(ImportExportModelAdmin):
    resource_class = BlockResource
    list_display = ("name",)
    search_fields = ("name",)


# Floor resource.
class FloorResource(resources.ModelResource):
    class Meta:
        model = Floor
        fields = ("id", "name", "block__name")


# Floor admin.
@admin.register(Floor)
class LocationAdmin(ImportExportModelAdmin):
    resource_class = FloorResource
    list_display = ("name", "block")
    search_fields = ("name", "block__name")
    list_filter = ("block",)


# Facility resources.
class FacilityResource(resources.ModelResource):
    class Meta:
        model = Facility
        fields = ("id", "name", "organization__name", "address", "phone_number")


# Facility admin.
@admin.register(Facility)
class FacilityAdmin(ImportExportModelAdmin):
    resource_class = FacilityResource
    list_display = ("name", "organization", "address", "phone_number")
    search_fields = ("name", "organization__name")
    list_filter = ("organization",)
