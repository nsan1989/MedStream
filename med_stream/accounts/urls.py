from django.urls import path
from .views import authView, logoutView, verifyOTPView, resendOTPView

urlpatterns = [
    path("register/", authView, name="register"),
    path("login/", authView, name="login"),
    path("logout/", logoutView, name="logout"),
    path("verify-otp", verifyOTPView, name="verify_otp"),
    path("resend_otp", resendOTPView, name="resend_otp"),
]
