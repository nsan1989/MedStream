from django.urls import path
from .views import OrganizationStaff, AllOrganizationView

urlpatterns = [
    path("org_staff/", OrganizationStaff, name="org_staff"),
    path("all_org/", AllOrganizationView, name="all_org"),
]
