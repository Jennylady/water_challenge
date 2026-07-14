from django.urls import path
from .views import AdminLoginAPIView, AdminLogoutAPIView, AdminMeAPIView, AdminRefreshTokenAPIView

urlpatterns = [
    path('login/', AdminLoginAPIView.as_view(), name='admin_login'),
    path('me/', AdminMeAPIView.as_view(), name='admin_me'),
    path('token/refresh/', AdminRefreshTokenAPIView.as_view(), name='admin_token_refresh'),
    path('logout/', AdminLogoutAPIView.as_view(), name='admin_logout'),
]
