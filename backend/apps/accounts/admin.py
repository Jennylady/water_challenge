from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Profile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User

    list_display = [
        "id",
        "email",
        "first_name",
        "last_name",
        "phone",
        "role",
        "email_verified",
        "is_active",
        "is_staff",
        "created_at",
    ]

    list_filter = [
        "role",
        "email_verified",
        "is_active",
        "is_staff",
        "is_superuser",
    ]

    search_fields = [
        "email",
        "first_name",
        "last_name",
        "phone",
    ]

    ordering = ["-created_at"]

    fieldsets = (
        (
            "Identifiants",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Informations personnelles",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "birth_date",
                )
            },
        ),
        (
            "Confirmation email",
            {
                "fields": (
                    "email_verified",
                )
            },
        ),
        (
            "Rôle et permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Dates importantes",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            "Créer un utilisateur",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone",
                    "birth_date",
                    "role",
                    "email_verified",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "scout_type",
        "section",
        "position",
        "faritra",
        "diosezy",
        "level",
        "points",
        "progression",
    ]

    list_filter = [
        "scout_type",
        "level",
        "faritra",
        "diosezy",
    ]

    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "section",
        "position",
        "faritra",
        "diosezy",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]