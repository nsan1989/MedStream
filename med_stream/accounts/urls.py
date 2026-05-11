from django.urls import path
from .views import authView

urlpatterns = [
    path("auth/register/", authView, name="register"),
    path("auth/login/", authView, name="login"),
]
