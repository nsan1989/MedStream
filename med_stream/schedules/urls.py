from django.urls import path
from .views import (
    AddDepartment,
    AddDoctor,
    load_departments,
    OpdRoom,
    OpdSchedule,
    DoctorSchedule,
    SchedulesView,
)

urlpatterns = [
    path("all_schedules/", SchedulesView, name="schedules"),
    path("settings/add_department/", AddDepartment, name="add_department"),
    path("settings/add_doctor/", AddDoctor, name="add_doctor"),
    path("settings/add_opd_room/", OpdRoom, name="add_opd_room"),
    path("settings/add_opd_schedule/", OpdSchedule, name="add_opd_schedule"),
    path("settings/add_doctor_schedule/", DoctorSchedule, name="add_doctor_schedule"),
    path("ajax/load-departments/", load_departments, name="ajax_load_departments"),
]
