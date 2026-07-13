from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from .backends import UserEmailBackend
from .models import Profile, User
from .tokens import UserRefreshToken


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id', 'avatar', 'scout_type', 'section', 'sampana', 'position',
            'fivondronana', 'faritra', 'diosezy', 'level', 'points',
            'progression', 'current_badge', 'bio', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'level', 'points', 'progression', 'current_badge',
            'created_at', 'updated_at',
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone',
            'birth_date', 'role', 'is_active', 'is_email_verified', 'profile',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    scout_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    section = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sampana = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    position = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fivondronana = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    faritra = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    diosezy = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Un compte existe déjà avec cette adresse email.')
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        validate_password(attrs.get('password'))
        return attrs

    def create(self, validated_data):
        profile_data = {
            'scout_type': validated_data.pop('scout_type', None),
            'section': validated_data.pop('section', None),
            'sampana': validated_data.pop('sampana', None),
            'position': validated_data.pop('position', None),
            'fivondronana': validated_data.pop('fivondronana', None),
            'faritra': validated_data.pop('faritra', None),
            'diosezy': validated_data.pop('diosezy', None),
        }
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            role=User.Role.AMBASSADOR,
            is_active=True,
            is_email_verified=False,
            **validated_data,
        )
        Profile.objects.create(user=user, **profile_data)
        return user


class ActivateEmailSerializer(serializers.Serializer):
    token = serializers.CharField(
        trim_whitespace=True,
        max_length=8192,
        help_text='Jeton unique chiffré reçu dans le lien de confirmation.',
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password')
        user = UserEmailBackend().authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError('Email ou mot de passe incorrect.')
        if not user.is_active:
            raise serializers.ValidationError('Ce compte est désactivé.')
        if not user.is_email_verified:
            raise serializers.ValidationError(
                'Veuillez confirmer votre adresse email avant de vous connecter.'
            )

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        refresh = UserRefreshToken.for_user_account(user)
        return {
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class ResendConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.lower().strip()
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('Aucun compte trouvé avec cette adresse email.')
        if user.is_email_verified:
            raise serializers.ValidationError('Cette adresse email est déjà confirmée.')
        self.user = user
        return value


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.refresh_token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        token = UserRefreshToken(self.refresh_token)
        token.blacklist()


class ProfileWriteSerializer(serializers.Serializer):
    avatar = serializers.ImageField(required=False, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=30)
    birth_date = serializers.DateField(required=False, allow_null=True)
    scout_type = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    section = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    sampana = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    position = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    fivondronana = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    faritra = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    diosezy = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    user_fields = ['first_name', 'last_name', 'phone', 'birth_date']
    profile_fields = [
        'avatar', 'scout_type', 'section', 'sampana', 'position',
        'fivondronana', 'faritra', 'diosezy', 'bio',
    ]

    def _save_user_fields(self, user, validated_data):
        changed_fields = []
        for field in self.user_fields:
            if field in validated_data:
                setattr(user, field, validated_data.pop(field))
                changed_fields.append(field)

        if changed_fields:
            user.save(update_fields=changed_fields + ['updated_at'])

    def _save_profile_fields(self, profile, validated_data):
        changed_fields = []
        for field in self.profile_fields:
            if field in validated_data:
                setattr(profile, field, validated_data[field])
                changed_fields.append(field)

        if changed_fields:
            profile.save(update_fields=changed_fields + ['updated_at'])

    def create(self, validated_data):
        user = self.context['user']
        self._save_user_fields(user, validated_data)
        profile, created = Profile.objects.get_or_create(user=user)
        self._save_profile_fields(profile, validated_data)
        self.created = created
        return user

    def update(self, instance, validated_data):
        user = instance
        self._save_user_fields(user, validated_data)
        profile, _ = Profile.objects.get_or_create(user=user)
        self._save_profile_fields(profile, validated_data)
        return user


class ProfileCreateSerializer(ProfileWriteSerializer):
    pass


class ProfileUpdateSerializer(ProfileWriteSerializer):
    pass


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        user = self.context['user']
        if not user.check_password(attrs.get('old_password')):
            raise serializers.ValidationError({'old_password': 'Ancien mot de passe incorrect.'})
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({
                'new_password_confirm': 'Les nouveaux mots de passe ne correspondent pas.'
            })
        validate_password(attrs.get('new_password'))
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password', 'updated_at'])
        return user
