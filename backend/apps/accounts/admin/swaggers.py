from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


DATE_TIME = openapi.Schema(
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATETIME,
)

ADMIN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'email': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
        ),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'full_name': openapi.Schema(type=openapi.TYPE_STRING),
        'role': openapi.Schema(type=openapi.TYPE_STRING),
        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'is_staff': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'is_superuser': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'created_at': DATE_TIME,
        'updated_at': DATE_TIME,
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
        'error': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    },
)

SUCCESS_MESSAGE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

ADMIN_LOGIN_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
        ),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

REFRESH_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['refresh'],
    properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING)},
)

ADMIN_LOGIN_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'admin': ADMIN_SCHEMA,
        'tokens': TOKENS_SCHEMA,
    },
)

ADMIN_ME_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'admin': ADMIN_SCHEMA,
    },
)

ADMIN_REFRESH_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'tokens': TOKENS_SCHEMA,
    },
)

ADMIN_LOGIN_SWAGGER = swagger_auto_schema(
    operation_summary='Connexion administrateur',
    request_body=ADMIN_LOGIN_REQUEST,
    responses={
        200: openapi.Response('Connexion réussie', ADMIN_LOGIN_RESPONSE),
        400: openapi.Response('Données invalides', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
    tags=['Accounts Admin'],
)

ADMIN_ME_SWAGGER = swagger_auto_schema(
    operation_summary='Profil administrateur connecté',
    security=[{'Bearer': []}],
    responses={
        200: openapi.Response('Admin connecté', ADMIN_ME_RESPONSE),
        401: openapi.Response('Non authentifié', ERROR_SCHEMA),
        403: openapi.Response('Token ou compte refusé', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
    tags=['Accounts Admin'],
)

ADMIN_REFRESH_SWAGGER = swagger_auto_schema(
    operation_summary='Rafraîchir le token administrateur',
    request_body=REFRESH_REQUEST,
    responses={
        200: openapi.Response('Token rafraîchi', ADMIN_REFRESH_RESPONSE),
        400: openapi.Response('Token invalide', ERROR_SCHEMA),
        403: openapi.Response('Compte désactivé', ERROR_SCHEMA),
        404: openapi.Response('Administrateur introuvable', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
    tags=['Accounts Admin'],
)

ADMIN_LOGOUT_SWAGGER = swagger_auto_schema(
    operation_summary='Déconnexion administrateur',
    security=[{'Bearer': []}],
    request_body=REFRESH_REQUEST,
    responses={
        200: openapi.Response('Déconnexion réussie', SUCCESS_MESSAGE_SCHEMA),
        400: openapi.Response('Token invalide', ERROR_SCHEMA),
        401: openapi.Response('Non authentifié', ERROR_SCHEMA),
        403: openapi.Response('Token non administrateur', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
    tags=['Accounts Admin'],
)
