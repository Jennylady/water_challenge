from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .managers import AdminUserManager


class AdminUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        SUPERADMIN = 'superadmin', 'Super Admin'

    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.ADMIN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = AdminUserManager()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def __str__(self):
        return f'{self.full_name} - {self.email}'

    class Meta:
        db_table = 'account_admin_user'

