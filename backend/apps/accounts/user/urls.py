from django.urls import path

from .views import (
    ActivateEmailAPIView,
    ChangePasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    MyProfileAPIView,
    ProfileCreateAPIView,
    ProfileDeleteAPIView,
    ProfileUpdateAPIView,
    RefreshTokenAPIView,
    RegisterAPIView,
    ResendConfirmationAPIView,
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='user_register'),
    path('activate/', ActivateEmailAPIView.as_view(), name='user_activate_email'),
    path('resend-confirmation/', ResendConfirmationAPIView.as_view(), name='user_resend_confirmation'),

    path('login/', LoginAPIView.as_view(), name='user_login'),
    path('token/refresh/', RefreshTokenAPIView.as_view(), name='user_token_refresh'),
    path('logout/', LogoutAPIView.as_view(), name='user_logout'),

    path('me/', MeAPIView.as_view(), name='user_me'),
    path('me/profile/', MyProfileAPIView.as_view(), name='user_profile_me'),
    path('me/profile/create/', ProfileCreateAPIView.as_view(), name='user_profile_create'),
    path('me/profile/update/', ProfileUpdateAPIView.as_view(), name='user_profile_update'),
    path('me/profile/delete/', ProfileDeleteAPIView.as_view(), name='user_profile_delete'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='user_change_password'),
]
