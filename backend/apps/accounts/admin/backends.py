from django.contrib.auth.backends import ModelBackend
from .models import AdminUser


class AdminEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email') or username
        if not email or not password:
            return None
        try:
            admin = AdminUser.objects.get(email=email.lower().strip())
        except AdminUser.DoesNotExist:
            return None
        if admin.check_password(password) and self.user_can_authenticate(admin):
            return admin
        return None

    def get_user(self, user_id):
        try:
            return AdminUser.objects.get(pk=user_id)
        except AdminUser.DoesNotExist:
            return None
