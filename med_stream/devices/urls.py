from django.urls import path
from .views import AddDevice, DeviceListView, load_blocks, load_floors

urlpatterns = [
    path("settings/add_device/", AddDevice, name="add_device"),
    path("all_devices/", DeviceListView, name="devices"),
    path("settings/ajax/load_blocks/", load_blocks, name="load_blocks"),
    path("settings/ajax/load_floors/", load_floors, name="load_floors"),
]
