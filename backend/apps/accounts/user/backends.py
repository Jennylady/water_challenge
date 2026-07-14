from .models import User


class UserEmailBackend:
    def authenticate(self, email=None, password=None):
        if not email or not password:
            return None
        try:
            user = User.objects.get(email=email.lower().strip())
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
