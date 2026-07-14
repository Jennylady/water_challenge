from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import AdminUser


@admin.register(AdminUser)
class AdminUserAdmin(DjangoUserAdmin):
    model = AdminUser
    list_display = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_superuser']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']

    fieldsets = (
        ('Identifiants', {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        ('Créer un administrateur', {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
