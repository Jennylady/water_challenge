from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import AdminUser
from rest_framework_simplejwt.tokens import RefreshToken


class AdminSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = AdminUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'is_staff', 'is_superuser',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password')
        admin = authenticate(username=email, password=password)

        if not admin:
            raise serializers.ValidationError('Email ou mot de passe incorrect.')
        if not admin.is_active:
            raise serializers.ValidationError('Ce compte administrateur est désactivé.')

        refresh = RefreshToken.for_user(admin)
        return {
            'admin': AdminSerializer(admin).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class AdminRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class AdminLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.refresh_token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        token = RefreshToken(self.refresh_token)
        token.blacklist()
