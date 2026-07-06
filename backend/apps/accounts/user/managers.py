from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")

        email = self.normalize_email(email).lower().strip()
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.password = ''

        user.save(using=self._db)
        return user

    def active(self):
        return self.filter(is_active=True)

    def verified(self):
        return self.filter(is_email_verified=True)
