from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

ADMIN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'full_name': openapi.Schema(type=openapi.TYPE_STRING),
        'role': openapi.Schema(type=openapi.TYPE_STRING),
        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'is_staff': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'is_superuser': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

TOKENS_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'access': openapi.Schema(type=openapi.TYPE_STRING),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

ERROR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'errors': openapi.Schema(type=openapi.TYPE_OBJECT),
    },
)

ADMIN_LOGIN_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

REFRESH_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['refresh'],
    properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING)},
)

ADMIN_LOGIN_SWAGGER = swagger_auto_schema(
    operation_summary='Connexion administrateur',
    operation_description='Connecte un administrateur Django et retourne des tokens JWT administrateur custom.',
    request_body=ADMIN_LOGIN_REQUEST,
    responses={
        200: openapi.Response('Connexion réussie', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'admin': ADMIN_SCHEMA,
                'tokens': TOKENS_SCHEMA,
            },
        )),
        400: openapi.Response('Erreur de validation', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
    tags=['Accounts Admin'],
)

ADMIN_ME_SWAGGER = swagger_auto_schema(
    operation_summary='Profil administrateur connecté',
    operation_description='Retourne les informations de l’administrateur connecté.',
    security=[{'Bearer': []}],
    responses={200: openapi.Response('Admin connecté', ADMIN_SCHEMA), 401: openapi.Response('Non authentifié', ERROR_SCHEMA)},
    tags=['Accounts Admin'],
)

ADMIN_REFRESH_SWAGGER = swagger_auto_schema(
    operation_summary='Refresh token administrateur',
    operation_description='Génère un nouvel access token administrateur depuis le refresh token custom.',
    request_body=REFRESH_REQUEST,
    responses={200: openapi.Response('Token rafraîchi', TOKENS_SCHEMA), 400: openapi.Response('Token invalide', ERROR_SCHEMA)},
    tags=['Accounts Admin'],
)

ADMIN_LOGOUT_SWAGGER = swagger_auto_schema(
    operation_summary='Déconnexion administrateur',
    operation_description='Blacklist le refresh token administrateur.',
    security=[{'Bearer': []}],
    request_body=REFRESH_REQUEST,
    responses={200: openapi.Response('Déconnexion réussie'), 400: openapi.Response('Token invalide', ERROR_SCHEMA)},
    tags=['Accounts Admin'],
)
