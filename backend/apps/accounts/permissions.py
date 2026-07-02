from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_role
        )


class IsValidatorRole(BasePermission):
    message = "Accès réservé aux validateurs."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_validator_role
        )