from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone

class User(models.Model):
    class Role(models.TextChoices):
        AMBASSADOR = 'ambassador', 'Ambassadeur'
        VALIDATOR = 'validator', 'Validateur'
        MODERATOR = 'moderator', 'Modérateur'

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.AMBASSADOR)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def __str__(self):
        return f'{self.full_name} - {self.email}'

    class Meta:
        db_table = 'account_user'


class Profile(models.Model):
    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Débutant'
        APPRENTICE = 'apprentice', 'Apprenti Ambassadeur'
        ACTIVE = 'active', 'Ambassadeur actif'
        LEADER = 'leader', 'Leader communautaire'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True)
    scout_type = models.CharField(max_length=100, blank=True, null=True)
    section = models.CharField(max_length=100, blank=True, null=True)
    sampana = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    fivondronana = models.CharField(max_length=150, blank=True, null=True)
    faritra = models.CharField(max_length=150, blank=True, null=True)
    diosezy = models.CharField(max_length=150, blank=True, null=True)
    level = models.CharField(max_length=30, choices=Level.choices, default=Level.BEGINNER)
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
        self.save(update_fields=['level'])

    def __str__(self):
        return f'Profil de {self.user.full_name}'

    class Meta:
        db_table = 'account_user_profile'


class UserOutstandingToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outstanding_tokens')
    jti = models.CharField(max_length=255, unique=True)
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    blacklisted = models.BooleanField(default=False)

    def is_expired(self):
        return self.expires_at <= timezone.now()

    class Meta:
        db_table = 'account_user_outstanding_token'
