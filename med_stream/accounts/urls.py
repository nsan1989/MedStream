from django.urls import path
from .views import authView, logoutView

urlpatterns = [
    path("register/", authView, name="register"),
    path("login/", authView, name="login"),
    path("logout/", logoutView, name="logout"),
]
