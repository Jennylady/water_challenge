from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    RegisterView,
    ActivateEmailView,
    ResendConfirmationEmailView,
    LoginView,
    LogoutView,
    MeView,
    ChangePasswordView,
)

urlpatterns = [
    # Register + confirmation email
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "activate/<str:uidb64>/<str:token>/",
        ActivateEmailView.as_view(),
        name="activate_email"
    ),
    path(
        "resend-confirmation/",
        ResendConfirmationEmailView.as_view(),
        name="resend_confirmation"
    ),

    # Auth JWT
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # Connected user
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]