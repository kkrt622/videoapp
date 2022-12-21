from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
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
    path("login", views.LoginView.as_view(), name="login"),
]
