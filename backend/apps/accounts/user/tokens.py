import uuid
from datetime import datetime, timezone

import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone as django_timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserOutstandingToken


class UserRefreshToken(RefreshToken):
    @classmethod
    def for_user_account(cls, user):
        if user is None:
            raise TokenError('User not provided')
        token = cls()
        token['account_type'] = 'user'
        token['app_user_id'] = user.id
        token['email'] = user.email
        token['role'] = user.role
        token['jti'] = str(uuid.uuid4())
        token.set_exp()
        expires_at = datetime.fromtimestamp(token['exp'], tz=timezone.utc)
        UserOutstandingToken.objects.create(
            user=user,
            jti=token['jti'],
            token=str(token),
            expires_at=expires_at,
        )
        return token

    def set_exp(self, from_time=None, lifetime=None):
        if from_time is None:
            from_time = django_timezone.now()
        if lifetime is None:
            lifetime = api_settings.REFRESH_TOKEN_LIFETIME
        super().set_exp(from_time=from_time, lifetime=lifetime)
        self.access_token.set_exp(
            from_time=from_time,
            lifetime=api_settings.ACCESS_TOKEN_LIFETIME,
        )

    def blacklist(self):
        try:
            outstanding_token = UserOutstandingToken.objects.get(jti=self['jti'])
            outstanding_token.blacklisted = True
            outstanding_token.save(update_fields=['blacklisted'])
        except UserOutstandingToken.DoesNotExist:
            raise TokenError('Token not found for blacklisting.')


class UserAccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.id)
            + six.text_type(timestamp)
            + six.text_type(user.is_email_verified)
            + six.text_type(user.email)
        )


account_activation_token = UserAccountActivationTokenGenerator()
