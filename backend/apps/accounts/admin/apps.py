from django.apps import AppConfig


class AccountsAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts.admin'
    label = 'accounts_admin'
    verbose_name = 'Comptes administrateurs Django'
