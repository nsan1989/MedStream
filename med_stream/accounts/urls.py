from django.urls import path
from .views import authView

urlpatterns = [
    path("auth/", authView, name="auth"),
]
