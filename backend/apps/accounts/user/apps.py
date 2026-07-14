from django.apps import AppConfig


class AccountsUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts.user'
    label = 'accounts_user'
    verbose_name = 'Comptes utilisateurs métier'
