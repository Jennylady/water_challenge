from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "avatar",
            "scout_type",
            "section",
            "sampana",
            "position",
            "fivondronana",
            "faritra",
            "diosezy",
            "level",
            "points",
            "progression",
            "current_badge",
            "bio",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "level",
            "points",
            "progression",
            "current_badge",
            "created_at",
            "updated_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "birth_date",
            "role",
            "email_verified",
            "profile",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "role",
            "email_verified",
            "created_at",
            "updated_at",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    scout_type = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    section = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    sampana = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    position = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    fivondronana = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    faritra = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    diosezy = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "password",
            "password_confirm",
            "scout_type",
            "section",
            "sampana",
            "position",
            "fivondronana",
            "faritra",
            "diosezy",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Un compte existe déjà avec cette adresse email."
            )

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "Les mots de passe ne correspondent pas."
            })

        validate_password(password)

        return attrs

    def create(self, validated_data):
        profile_data = {
            "scout_type": validated_data.pop("scout_type", None) or Profile.ScoutType.SCOUT,
            "section": validated_data.pop("section", None),
            "sampana": validated_data.pop("sampana", None),
            "position": validated_data.pop("position", None),
            "fivondronana": validated_data.pop("fivondronana", None),
            "faritra": validated_data.pop("faritra", None),
            "diosezy": validated_data.pop("diosezy", None),
        }

        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            role=User.Role.AMBASSADOR,
            email_verified=False,
            is_active=True,
            **validated_data,
        )

        Profile.objects.create(
            user=user,
            **profile_data,
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        email = attrs.get("email", "").lower().strip()
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "Email ou mot de passe incorrect."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Ce compte est désactivé."
            )

        if not user.email_verified:
            raise serializers.ValidationError(
                "Veuillez confirmer votre adresse email avant de vous connecter."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class UpdateMeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "profile",
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if profile_data is not None:
            profile, _ = Profile.objects.get_or_create(user=instance)

            for attr, value in profile_data.items():
                setattr(profile, attr, value)

            profile.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        user = self.context["request"].user

        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")

        if not user.check_password(old_password):
            raise serializers.ValidationError({
                "old_password": "Ancien mot de passe incorrect."
            })

        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                "new_password_confirm": "Les nouveaux mots de passe ne correspondent pas."
            })

        validate_password(new_password, user=user)

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()

        return user


class ResendConfirmationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.lower().strip()

        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Aucun compte trouvé avec cette adresse email."
            )

        if user.email_verified:
            raise serializers.ValidationError(
                "Cette adresse email est déjà confirmée."
            )

        self.user = user

        return value


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.refresh_token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        token = RefreshToken(self.refresh_token)
        token.blacklist()