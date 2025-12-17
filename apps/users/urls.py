from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path(
        "verify-email/<uuid:token>/", views.verify_email, name="verify_email"
    ),
    path(
        "password-reset/request/",
        views.request_password_reset,
        name="request_password_reset",
    ),
    path(
        "password-reset/confirm/",
        views.confirm_password_reset,
        name="confirm_password_reset",
    ),
    path("password/change/", views.change_password, name="change_password"),
]
