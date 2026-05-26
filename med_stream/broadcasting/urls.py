from django.urls import path

from .views import BroadcastView, StopBroadcastView, AllBroadcastView

urlpatterns = [
    path("", BroadcastView, name="broadcasts"),
    path("stop/<uuid:device_id>/", StopBroadcastView, name="stop_broadcast"),
    path("all_broadcasts/", AllBroadcastView, name="all_broadcasts"),
]
