from django.urls import path
from . import views

app_name = "app_users"

urlpatterns = [
    path("register/", views.registration_view, name="register"),
    path(
        "registration-success/", views.registration_success, name="registration_success"
    ),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("verify-email/<uuid:token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.resend_verification_email, name="resend_verification"),
]
