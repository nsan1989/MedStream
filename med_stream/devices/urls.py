from django.urls import path
from .views import (
    AddDevice,
    DeviceListView,
    load_blocks,
    load_floors,
    DeviceNextCommand,
    DeviceCommandAck,
    DevicePlayerAutoPage,
    DevicePlayerPage,
)

urlpatterns = [
    path("settings/add_device/", AddDevice, name="add_device"),
    path("all_devices/", DeviceListView, name="devices"),
    path("settings/ajax/load_blocks/", load_blocks, name="load_blocks"),
    path("settings/ajax/load_floors/", load_floors, name="load_floors"),
    path(
        "player/<uuid:device_id>/next-command/",
        DeviceNextCommand,
        name="device_next_command",
    ),
    path("player/<uuid:device_id>/ack/", DeviceCommandAck, name="device_command_ack"),
    path("player/auto/", DevicePlayerAutoPage, name="device_player_auto"),
    path("player/<uuid:device_id>/", DevicePlayerPage, name="device_player_page"),
]
