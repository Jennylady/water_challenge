from django.conf import settings
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UpdateMeSerializer,
    ChangePasswordSerializer,
    ResendConfirmationEmailSerializer,
    LogoutSerializer,
)
from .tokens import email_verification_token
from .utils import send_email_confirmation


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        confirmation_link = send_email_confirmation(user)

        response_data = {
            "message": "Compte créé avec succès. Veuillez confirmer votre email avant de vous connecter.",
            "user": UserSerializer(user).data,
        }

        if settings.DEBUG:
            response_data["dev_confirmation_link"] = confirmation_link

        return Response(response_data, status=status.HTTP_201_CREATED)


class ActivateEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response(
                {
                    "message": "Lien de confirmation invalide."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.email_verified:
            return Response(
                {
                    "message": "Cette adresse email est déjà confirmée."
                },
                status=status.HTTP_200_OK
            )

        if not email_verification_token.check_token(user, token):
            return Response(
                {
                    "message": "Lien de confirmation invalide ou expiré."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.email_verified = True
        user.save(update_fields=["email_verified"])

        return Response(
            {
                "message": "Email confirmé avec succès. Vous pouvez maintenant vous connecter."
            },
            status=status.HTTP_200_OK
        )


class ResendConfirmationEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResendConfirmationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        confirmation_link = send_email_confirmation(serializer.user)

        response_data = {
            "message": "Un nouveau lien de confirmation a été envoyé."
        }

        if settings.DEBUG:
            response_data["dev_confirmation_link"] = confirmation_link

        return Response(response_data, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "message": "Connexion réussie.",
                "user": serializer.validated_data["user"],
                "tokens": {
                    "access": serializer.validated_data["access"],
                    "refresh": serializer.validated_data["refresh"],
                }
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except TokenError:
            return Response(
                {
                    "message": "Refresh token invalide ou déjà blacklisté."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Déconnexion réussie."
            },
            status=status.HTTP_200_OK
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        serializer = UpdateMeSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Profil mis à jour avec succès.",
                "user": UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK
        )

    def put(self, request):
        serializer = UpdateMeSerializer(
            request.user,
            data=request.data,
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Profil mis à jour avec succès.",
                "user": UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Mot de passe modifié avec succès."
            },
            status=status.HTTP_200_OK
        )