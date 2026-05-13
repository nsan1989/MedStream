from django.urls import path
from .views import SuperAdminDashboard, AdminDashboard, StaffDashboard

urlpatterns = [
    path("super_admin_dashboard/", SuperAdminDashboard, name="super_admin_dashboard"),
    path("admin_dashboard/", AdminDashboard, name="admin_dashboard"),
    path("staff_dashboard", StaffDashboard, name="staff_dashboard"),
]
