from django.contrib import admin
from .models import Profile, User, UserOutstandingToken


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_email_verified', 'created_at']
    list_filter = ['role', 'is_active', 'is_email_verified']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    readonly_fields = ['password', 'last_login', 'created_at', 'updated_at']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'scout_type', 'section', 'position', 'faritra', 'diosezy', 'level', 'points']
    list_filter = ['level', 'faritra', 'diosezy']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'faritra']


@admin.register(UserOutstandingToken)
class UserOutstandingTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'jti', 'blacklisted', 'created_at', 'expires_at']
    list_filter = ['blacklisted', 'created_at', 'expires_at']
    search_fields = ['user__email', 'jti']
    readonly_fields = ['user', 'jti', 'token', 'created_at', 'expires_at']
