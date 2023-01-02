from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "temp_registration",
        views.TempRegistrationView.as_view(),
        name="temp_registration",
    ),
    path(
        "temp_registration_done/<user_id>",
        views.TempRegistrationDoneView.as_view(),
        name="temp_registration_done",
    ),
    path(
        "signup/<user_id>",
        views.SignUpView.as_view(),
        name="signup",
    ),
    path(
        "password_reset",
        views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset_confirmation/<user_id>",
        views.PasswordResetConfirmationView.as_view(),
        name="password_reset_confirmation",
    ),
    path(
        "password_change/<user_id>",
        views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path("login", views.LoginView.as_view(), name="login"),
    path("video_upload", views.VideoUploadView.as_view(), name="video_upload"),
]
