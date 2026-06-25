from django.urls import path
from .views import (
    AddStaff,
    AddFacility,
    AddBlock,
    AddFloor,
    BlockList,
    FloorList,
    FacilityList,
)

urlpatterns = [
    path("settings/add_staff/", AddStaff, name="add_staff"),
    path("settings/add_facility/", AddFacility, name="add_facility"),
    path("settings/add_block/", AddBlock, name="add_block"),
    path("settings/add_floor/", AddFloor, name="add_floor"),
    path("blocks/", BlockList, name="block"),
    path("floors/", FloorList, name="floor"),
    path("facilities/", FacilityList, name="facilities"),
]
