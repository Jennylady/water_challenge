import traceback

from django.conf import settings
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, User, UserOutstandingToken
from .permissions import IsAuthenticatedUser
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    ProfileCreateSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    ResendConfirmationSerializer,
    UserSerializer,
)
from .swaggers import (
    ACTIVATE_EMAIL_SWAGGER,
    CHANGE_PASSWORD_SWAGGER,
    LOGIN_SWAGGER,
    LOGOUT_SWAGGER,
    ME_SWAGGER,
    PROFILE_CREATE_SWAGGER,
    PROFILE_DELETE_SWAGGER,
    PROFILE_ME_SWAGGER,
    PROFILE_UPDATE_SWAGGER,
    REFRESH_SWAGGER,
    REGISTER_SWAGGER,
    RESEND_CONFIRMATION_SWAGGER,
)
from .tokens import account_activation_token
from .utils import send_account_activation_email


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @REGISTER_SWAGGER
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'message': 'Données invalides.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()
            activation_link = send_account_activation_email(user)

            response_data = {
                'success': True,
                'message': 'Compte créé avec succès. Veuillez confirmer votre email avant de vous connecter.',
                'user': UserSerializer(user).data,
            }
            if settings.DEBUG:
                response_data['dev_activation_link'] = activation_link
                response_data['dev_confirmation_link'] = activation_link

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors de la création du compte.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ActivateEmailAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @ACTIVATE_EMAIL_SWAGGER
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if user.is_email_verified:
                return Response(
                    {'success': True, 'message': 'Cette adresse email est déjà confirmée.'},
                    status=status.HTTP_200_OK,
                )

            if not account_activation_token.check_token(user, token):
                return Response(
                    {'success': False, 'message': 'Lien de confirmation invalide ou expiré.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.is_email_verified = True
            user.save(update_fields=['is_email_verified', 'updated_at'])
            return Response(
                {'success': True, 'message': 'Email confirmé avec succès. Vous pouvez maintenant vous connecter.'},
                status=status.HTTP_200_OK,
            )
        except Exception:
            traceback.print_exc()
            return Response(
                {'success': False, 'message': 'Lien de confirmation invalide.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResendConfirmationAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @RESEND_CONFIRMATION_SWAGGER
    def post(self, request):
        try:
            serializer = ResendConfirmationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'message': 'Données invalides.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            activation_link = send_account_activation_email(serializer.user)
            response_data = {'success': True, 'message': 'Un nouveau lien de confirmation a été envoyé.'}
            if settings.DEBUG:
                response_data['dev_activation_link'] = activation_link
                response_data['dev_confirmation_link'] = activation_link
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': "Erreur interne lors du renvoi de l'email de confirmation.",
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @LOGIN_SWAGGER
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'message': 'Données invalides.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    'success': True,
                    'message': 'Connexion réussie.',
                    'user': serializer.validated_data['user'],
                    'tokens': {
                        'access': serializer.validated_data['access'],
                        'refresh': serializer.validated_data['refresh'],
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors de la connexion.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @REFRESH_SWAGGER
    def post(self, request):
        try:
            serializer = RefreshTokenSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'message': 'Données invalides.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refresh_token = RefreshToken(serializer.validated_data['refresh'])
            jti = refresh_token.get('jti')
            outstanding = UserOutstandingToken.objects.get(jti=jti, blacklisted=False)
            user = outstanding.user

            if not user.is_active:
                return Response(
                    {'success': False, 'message': 'Compte utilisateur désactivé.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            access = refresh_token.access_token
            return Response(
                {
                    'success': True,
                    'message': 'Token rafraîchi avec succès.',
                    'tokens': {'access': str(access), 'refresh': str(refresh_token)},
                },
                status=status.HTTP_200_OK,
            )
        except (TokenError, UserOutstandingToken.DoesNotExist):
            return Response(
                {'success': False, 'message': 'Refresh token invalide ou blacklisté.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors du rafraîchissement du token.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticatedUser]
    authentication_classes = []

    @LOGOUT_SWAGGER
    def post(self, request):
        try:
            serializer = LogoutSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'message': 'Données invalides.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                {'success': True, 'message': 'Déconnexion réussie.'},
                status=status.HTTP_200_OK,
            )
        except TokenError:
            return Response(
                {'success': False, 'message': 'Refresh token invalide ou déjà blacklisté.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors de la déconnexion.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MeAPIView(APIView):
    permission_classes = [IsAuthenticatedUser]
    authentication_classes = []

    @ME_SWAGGER
    def get(self, request):
        try:
            return Response(
                {'success': True, 'user': UserSerializer(request.app_user).data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors de la récupération du compte.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyProfileAPIView(APIView):
    permission_classes = [IsAuthenticatedUser]
    authentication_classes = []

    @PROFILE_ME_SWAGGER
    def get(self, request):
        try:
            profile, _ = Profile.objects.get_or_create(user=request.app_user)
            return Response(
                {
                    'success': True,
                    'user': UserSerializer(request.app_user).data,
                    'profile': ProfileSerializer(profile).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors de la récupération du profil.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedUser]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @PROFILE_CREATE_SWAGGER
    def post(self, request):
        try:
            serializer = ProfileCreateSerializer(data=request.data, context={'user': request.app_user})
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'message': 'Données invalides.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()
            created = getattr(serializer, 'created', False)
            profile = user.profile
            message = 'Profil créé avec succès.' if created else 'Profil déjà existant, mis à jour avec succès.'
            response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK

            return Response(
                {
                    'success': True,
                    'message': message,
                    'user': UserSerializer(user).data,
                    'profile': ProfileSerializer(profile).data,
                },
                status=response_status,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors de la création du profil.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticatedUser]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @PROFILE_UPDATE_SWAGGER
    def patch(self, request):
        try:
            serializer = ProfileUpdateSerializer(request.app_user, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'message': 'Données invalides.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = serializer.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            return Response(
                {
                    'success': True,
                    'message': 'Profil mis à jour avec succès.',
                    'user': UserSerializer(user).data,
                    'profile': ProfileSerializer(profile).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors de la mise à jour du profil.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileDeleteAPIView(APIView):
    permission_classes = [IsAuthenticatedUser]
    authentication_classes = []

    @PROFILE_DELETE_SWAGGER
    def delete(self, request):
        try:
            try:
                profile = request.app_user.profile
            except Profile.DoesNotExist:
                return Response(
                    {'success': False, 'message': 'Profil introuvable.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if profile.avatar:
                profile.avatar.delete(save=False)

            profile.delete()
            return Response(
                {'success': True, 'message': 'Profil supprimé avec succès.'},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors de la suppression du profil.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticatedUser]
    authentication_classes = []

    @CHANGE_PASSWORD_SWAGGER
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data, context={'user': request.app_user})
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'message': 'Données invalides.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                {'success': True, 'message': 'Mot de passe modifié avec succès.'},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {
                    'success': False,
                    'message': 'Erreur interne lors du changement de mot de passe.',
                    'error': str(e) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
