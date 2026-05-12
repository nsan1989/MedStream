from django.urls import path
from .views import authView

urlpatterns = [
    path("register/", authView, name="register"),
    path("login/", authView, name="login"),
]
