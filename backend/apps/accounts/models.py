from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.SUPERADMIN)
        extra_fields.setdefault("email_verified", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        AMBASSADOR = "ambassador", "Ambassador"
        VALIDATOR = "validator", "Validator"
        ADMIN = "admin", "Admin"
        SUPERADMIN = "superadmin", "Super Admin"

    username = None

    email = models.EmailField(_("adresse email"), unique=True)
    first_name = models.CharField(_("prénom"), max_length=150)
    last_name = models.CharField(_("nom"), max_length=150)
    phone = models.CharField(_("téléphone"), max_length=30, blank=True, null=True)
    birth_date = models.DateField(_("date de naissance"), blank=True, null=True)

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.AMBASSADOR
    )

    email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} - {self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin_role(self):
        return self.role in [
            self.Role.ADMIN,
            self.Role.SUPERADMIN,
        ]

    @property
    def is_validator_role(self):
        return self.role in [
            self.Role.VALIDATOR,
            self.Role.ADMIN,
            self.Role.SUPERADMIN,
        ]


class Profile(models.Model):
    class ScoutType(models.TextChoices):
        SCOUT = "scout", "Scout"
        NON_SCOUT = "non_scout", "Non scout"

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Débutant"
        APPRENTICE = "apprentice", "Apprenti Ambassadeur"
        ACTIVE = "active", "Ambassadeur actif"
        LEADER = "leader", "Leader communautaire"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True
    )

    scout_type = models.CharField(
        max_length=30,
        choices=ScoutType.choices,
        default=ScoutType.SCOUT
    )

    section = models.CharField(max_length=100, blank=True, null=True)
    sampana = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)

    fivondronana = models.CharField(max_length=150, blank=True, null=True)
    faritra = models.CharField(max_length=150, blank=True, null=True)
    diosezy = models.CharField(max_length=150, blank=True, null=True)

    level = models.CharField(
        max_length=30,
        choices=Level.choices,
        default=Level.BEGINNER
    )

    points = models.PositiveIntegerField(default=0)
    progression = models.PositiveIntegerField(default=0)

    current_badge = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_level(self):
        if self.points >= 700:
            self.level = self.Level.LEADER
        elif self.points >= 300:
            self.level = self.Level.ACTIVE
        elif self.points >= 100:
            self.level = self.Level.APPRENTICE
        else:
            self.level = self.Level.BEGINNER

        self.save(update_fields=["level"])

    def __str__(self):
        return f"Profil de {self.user.full_name}"