from django.urls import path
from .views import AddDepartment, AddDoctor, load_departments

urlpatterns = [
    path("settings/add_department/", AddDepartment, name="add_department"),
    path("settings/add_doctor/", AddDoctor, name="add_doctor"),
    path("ajax/load-departments/", load_departments, name="ajax_load_departments"),
]
