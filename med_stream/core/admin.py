from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Department


# Department resources.
class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Department
        fields = ("id", "name")


# Department admin.
@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    list_display = ("id", "name")
    search_fields = ("name",)
