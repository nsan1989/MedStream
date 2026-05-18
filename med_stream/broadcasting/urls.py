from django.urls import path

from .views import BroadcastView


urlpatterns = [
    path("", BroadcastView, name="broadcasts"),
]
