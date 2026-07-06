from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

ERROR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'errors': openapi.Schema(type=openapi.TYPE_OBJECT),
    },
)

PROFILE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'avatar': openapi.Schema(type=openapi.TYPE_STRING),
        'scout_type': openapi.Schema(type=openapi.TYPE_STRING),
        'section': openapi.Schema(type=openapi.TYPE_STRING),
        'sampana': openapi.Schema(type=openapi.TYPE_STRING),
        'position': openapi.Schema(type=openapi.TYPE_STRING),
        'fivondronana': openapi.Schema(type=openapi.TYPE_STRING),
        'faritra': openapi.Schema(type=openapi.TYPE_STRING),
        'diosezy': openapi.Schema(type=openapi.TYPE_STRING),
        'level': openapi.Schema(type=openapi.TYPE_STRING),
        'points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'progression': openapi.Schema(type=openapi.TYPE_INTEGER),
        'current_badge': openapi.Schema(type=openapi.TYPE_STRING),
        'bio': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

USER_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'full_name': openapi.Schema(type=openapi.TYPE_STRING),
        'phone': openapi.Schema(type=openapi.TYPE_STRING),
        'birth_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        'role': openapi.Schema(type=openapi.TYPE_STRING),
        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'profile': PROFILE_SCHEMA,
    },
)

TOKENS_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'access': openapi.Schema(type=openapi.TYPE_STRING),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

REGISTER_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'first_name', 'last_name', 'password', 'password_confirm'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'phone': openapi.Schema(type=openapi.TYPE_STRING),
        'birth_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
        'password_confirm': openapi.Schema(type=openapi.TYPE_STRING),
        'scout_type': openapi.Schema(type=openapi.TYPE_STRING),
        'section': openapi.Schema(type=openapi.TYPE_STRING),
        'sampana': openapi.Schema(type=openapi.TYPE_STRING),
        'position': openapi.Schema(type=openapi.TYPE_STRING),
        'fivondronana': openapi.Schema(type=openapi.TYPE_STRING),
        'faritra': openapi.Schema(type=openapi.TYPE_STRING),
        'diosezy': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

LOGIN_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

EMAIL_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)},
)

REFRESH_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['refresh'],
    properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING)},
)

CHANGE_PASSWORD_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['old_password', 'new_password', 'new_password_confirm'],
    properties={
        'old_password': openapi.Schema(type=openapi.TYPE_STRING),
        'new_password': openapi.Schema(type=openapi.TYPE_STRING),
        'new_password_confirm': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

REGISTER_SWAGGER = swagger_auto_schema(
    operation_summary='Inscription utilisateur métier',
    operation_description='Crée un compte ambassadeur et envoie un email de confirmation.',
    request_body=REGISTER_REQUEST,
    responses={201: openapi.Response('Compte créé', USER_SCHEMA), 400: openapi.Response('Erreur validation', ERROR_SCHEMA)},
    tags=['Accounts User'],
)

ACTIVATE_EMAIL_SWAGGER = swagger_auto_schema(
    operation_summary='Activation email utilisateur',
    operation_description='Active le compte métier via uidb64 et token.',
    responses={200: openapi.Response('Email confirmé'), 400: openapi.Response('Lien invalide', ERROR_SCHEMA)},
    tags=['Accounts User'],
)

RESEND_CONFIRMATION_SWAGGER = swagger_auto_schema(
    operation_summary='Renvoyer email de confirmation',
    request_body=EMAIL_REQUEST,
    responses={200: openapi.Response('Email envoyé'), 400: openapi.Response('Erreur validation', ERROR_SCHEMA)},
    tags=['Accounts User'],
)

LOGIN_SWAGGER = swagger_auto_schema(
    operation_summary='Connexion utilisateur métier',
    request_body=LOGIN_REQUEST,
    responses={200: openapi.Response('Connexion réussie', openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'user': USER_SCHEMA,
            'tokens': TOKENS_SCHEMA,
        },
    )), 400: openapi.Response('Erreur validation', ERROR_SCHEMA)},
    tags=['Accounts User'],
)

REFRESH_SWAGGER = swagger_auto_schema(
    operation_summary='Refresh token utilisateur métier',
    request_body=REFRESH_REQUEST,
    responses={200: openapi.Response('Token rafraîchi', TOKENS_SCHEMA), 400: openapi.Response('Token invalide', ERROR_SCHEMA)},
    tags=['Accounts User'],
)

LOGOUT_SWAGGER = swagger_auto_schema(
    operation_summary='Déconnexion utilisateur métier',
    security=[{'Bearer': []}],
    request_body=REFRESH_REQUEST,
    responses={200: openapi.Response('Déconnexion réussie'), 400: openapi.Response('Token invalide', ERROR_SCHEMA)},
    tags=['Accounts User'],
)

ME_SWAGGER = swagger_auto_schema(
    operation_summary='Utilisateur métier connecté',
    security=[{'Bearer': []}],
    responses={200: openapi.Response('Utilisateur connecté', USER_SCHEMA), 401: openapi.Response('Non authentifié', ERROR_SCHEMA)},
    tags=['Accounts User'],
)

PROFILE_UPDATE_MANUAL_PARAMETERS = [
    openapi.Parameter('avatar', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False, description='Avatar utilisateur'),
    openapi.Parameter('first_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('last_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('phone', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('birth_date', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='YYYY-MM-DD'),
    openapi.Parameter('scout_type', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('section', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('sampana', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('position', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('fivondronana', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('faritra', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('diosezy', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('bio', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
]

PROFILE_UPDATE_SWAGGER = swagger_auto_schema(
    operation_summary='Modifier profil utilisateur métier',
    operation_description='Endpoint multipart. Swagger utilise uniquement manual_parameters, jamais request_body.',
    manual_parameters=PROFILE_UPDATE_MANUAL_PARAMETERS,
    consumes=['multipart/form-data'],
    security=[{'Bearer': []}],
    responses={200: openapi.Response('Profil modifié', USER_SCHEMA), 400: openapi.Response('Erreur validation', ERROR_SCHEMA)},
    tags=['Accounts User'],
)

CHANGE_PASSWORD_SWAGGER = swagger_auto_schema(
    operation_summary='Changer mot de passe utilisateur métier',
    request_body=CHANGE_PASSWORD_REQUEST,
    security=[{'Bearer': []}],
    responses={200: openapi.Response('Mot de passe modifié'), 400: openapi.Response('Erreur validation', ERROR_SCHEMA)},
    tags=['Accounts User'],
)
