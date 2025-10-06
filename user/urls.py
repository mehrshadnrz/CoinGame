from django.urls import path

from user.views import (
    ChangePasswordView,
    CustomLoginView,
    LogoutView,
    MeView,
    SignupView,
    UpdateProfileView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("update-profile/", UpdateProfileView.as_view(), name="update-profile"),
]
