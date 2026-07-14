import traceback

from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AdminUser
from .serializers import (
    AdminLoginSerializer,
    AdminLogoutSerializer,
    AdminRefreshSerializer,
    AdminSerializer,
)
from .swaggers import (
    ADMIN_LOGIN_SWAGGER,
    ADMIN_LOGOUT_SWAGGER,
    ADMIN_ME_SWAGGER,
    ADMIN_REFRESH_SWAGGER,
)


class AdminLoginAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @ADMIN_LOGIN_SWAGGER
    def post(self, request):
        try:
            serializer = AdminLoginSerializer(
                data=request.data,
                context={"request": request},
            )

            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Données invalides.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Connexion administrateur réussie.",
                    "admin": serializer.validated_data["admin"],
                    "tokens": {
                        "access": serializer.validated_data["access"],
                        "refresh": serializer.validated_data["refresh"],
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    "success": False,
                    "message": "Erreur interne lors de la connexion administrateur.",
                    "error": str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminMeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @ADMIN_ME_SWAGGER
    def get(self, request):
        try:
            admin = request.user

            if not admin or not admin.is_authenticated:
                return Response(
                    {
                        "success": False,
                        "message": "Administrateur non authentifié.",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if not isinstance(admin, AdminUser):
                return Response(
                    {
                        "success": False,
                        "message": "Token invalide pour un compte administrateur.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if not admin.is_active:
                return Response(
                    {
                        "success": False,
                        "message": "Ce compte administrateur est désactivé.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(
                {
                    "success": True,
                    "admin": AdminSerializer(admin).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    "success": False,
                    "message": "Erreur interne lors de la récupération du profil administrateur.",
                    "error": str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminRefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @ADMIN_REFRESH_SWAGGER
    def post(self, request):
        try:
            serializer = AdminRefreshSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Données invalides.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refresh_value = serializer.validated_data["refresh"]
            refresh_token = RefreshToken(refresh_value)

            user_id_claim = api_settings.USER_ID_CLAIM
            user_id_field = api_settings.USER_ID_FIELD

            admin_id = refresh_token.get(user_id_claim)

            if not admin_id:
                return Response(
                    {
                        "success": False,
                        "message": "Refresh token invalide.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                admin = AdminUser.objects.get(**{user_id_field: admin_id})
            except AdminUser.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": "Administrateur introuvable.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not admin.is_active:
                return Response(
                    {
                        "success": False,
                        "message": "Ce compte administrateur est désactivé.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            access_token = refresh_token.access_token

            return Response(
                {
                    "success": True,
                    "message": "Token administrateur rafraîchi avec succès.",
                    "tokens": {
                        "access": str(access_token),
                        "refresh": str(refresh_token),
                    },
                },
                status=status.HTTP_200_OK,
            )

        except TokenError:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token invalide, expiré ou blacklisté.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    "success": False,
                    "message": "Erreur interne lors du rafraîchissement du token administrateur.",
                    "error": str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @ADMIN_LOGOUT_SWAGGER
    def post(self, request):
        try:
            admin = request.user

            if not admin or not admin.is_authenticated:
                return Response(
                    {
                        "success": False,
                        "message": "Administrateur non authentifié.",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if not isinstance(admin, AdminUser):
                return Response(
                    {
                        "success": False,
                        "message": "Token invalide pour un compte administrateur.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = AdminLogoutSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Données invalides.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Déconnexion administrateur réussie.",
                },
                status=status.HTTP_200_OK,
            )

        except TokenError:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token invalide ou déjà blacklisté.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    "success": False,
                    "message": "Erreur interne lors de la déconnexion administrateur.",
                    "error": str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )