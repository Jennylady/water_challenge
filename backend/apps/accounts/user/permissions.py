from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission
from helpers.helper import get_token_from_request, get_user


class IsAuthenticatedUser(BasePermission):
    message = 'Authentification utilisateur requise.'

    def has_permission(self, request, view):
        token = get_token_from_request(request)
        if not token:
            return False
        user = get_user(token)
        if user is None or isinstance(user, AnonymousUser):
            return False
        if not user.is_active:
            return False
        request.app_user = user
        return True


class IsValidatorUser(BasePermission):
    message = 'Accès réservé aux validateurs.'

    def has_permission(self, request, view):
        token = get_token_from_request(request)
        if not token:
            return False
        user = get_user(token)
        if user is None or not user.is_active:
            return False
        request.app_user = user
        return user.role in ['validator', 'moderator']


class IsModeratorUser(BasePermission):
    message = 'Accès réservé aux modérateurs.'

    def has_permission(self, request, view):
        token = get_token_from_request(request)
        if not token:
            return False
        user = get_user(token)
        if user is None or not user.is_active:
            return False
        request.app_user = user
        return user.role == 'moderator'
