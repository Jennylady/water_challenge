from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


DATE = openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE)
DATE_NULLABLE = openapi.Schema(
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATE,
    x_nullable=True,
)
DATE_TIME = openapi.Schema(
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATETIME,
)
STRING_NULLABLE = openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True)


ERROR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'errors': openapi.Schema(type=openapi.TYPE_OBJECT),
        'error': STRING_NULLABLE,
    },
)

SUCCESS_MESSAGE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

TOKEN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'access': openapi.Schema(type=openapi.TYPE_STRING),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

PROFILE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'avatar': STRING_NULLABLE,
        'scout_type': STRING_NULLABLE,
        'section': STRING_NULLABLE,
        'sampana': STRING_NULLABLE,
        'position': STRING_NULLABLE,
        'fivondronana': STRING_NULLABLE,
        'faritra': STRING_NULLABLE,
        'diosezy': STRING_NULLABLE,
        'level': openapi.Schema(type=openapi.TYPE_STRING),
        'points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'progression': openapi.Schema(type=openapi.TYPE_INTEGER),
        'current_badge': STRING_NULLABLE,
        'bio': STRING_NULLABLE,
        'created_at': DATE_TIME,
        'updated_at': DATE_TIME,
    },
)

USER_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'email': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
        ),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'full_name': openapi.Schema(type=openapi.TYPE_STRING),
        'phone': STRING_NULLABLE,
        'birth_date': DATE_NULLABLE,
        'role': openapi.Schema(type=openapi.TYPE_STRING),
        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'profile': PROFILE_SCHEMA,
        'created_at': DATE_TIME,
        'updated_at': DATE_TIME,
    },
)

REGISTER_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'first_name', 'last_name', 'password', 'password_confirm'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
        ),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'phone': STRING_NULLABLE,
        'birth_date': DATE_NULLABLE,
        'password': openapi.Schema(type=openapi.TYPE_STRING, min_length=8),
        'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, min_length=8),
        'scout_type': STRING_NULLABLE,
        'section': STRING_NULLABLE,
        'sampana': STRING_NULLABLE,
        'position': STRING_NULLABLE,
        'fivondronana': STRING_NULLABLE,
        'faritra': STRING_NULLABLE,
        'diosezy': STRING_NULLABLE,
    },
)

LOGIN_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
        ),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

ACTIVATE_EMAIL_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['token'],
    properties={
        'token': openapi.Schema(
            type=openapi.TYPE_STRING,
            max_length=8192,
            description='Jeton chiffré reçu dans le lien de confirmation.',
        ),
    },
)

EMAIL_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
        ),
    },
)

REFRESH_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['refresh'],
    properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING)},
)

CHANGE_PASSWORD_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['old_password', 'new_password', 'new_password_confirm'],
    properties={
        'old_password': openapi.Schema(type=openapi.TYPE_STRING),
        'new_password': openapi.Schema(type=openapi.TYPE_STRING, min_length=8),
        'new_password_confirm': openapi.Schema(
            type=openapi.TYPE_STRING, min_length=8
        ),
    },
)

PROFILE_MANUAL_PARAMETERS = [
    openapi.Parameter(
        'avatar', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False
    ),
    openapi.Parameter(
        'first_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'last_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'phone', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'birth_date', openapi.IN_FORM, type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE, required=False,
    ),
    openapi.Parameter(
        'scout_type', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'section', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'sampana', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'position', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'fivondronana', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'faritra', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'diosezy', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
    openapi.Parameter(
        'bio', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
    ),
]

USER_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'user': USER_SCHEMA,
    },
)

PROFILE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'user': USER_SCHEMA,
        'profile': PROFILE_SCHEMA,
    },
)

PROFILE_MUTATION_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'user': USER_SCHEMA,
        'profile': PROFILE_SCHEMA,
    },
)


REGISTER_SWAGGER = swagger_auto_schema(
    operation_summary='Créer un compte utilisateur métier',
    tags=['User - Auth'],
    request_body=REGISTER_REQUEST_SCHEMA,
    responses={
        201: openapi.Response('Compte créé', SUCCESS_MESSAGE_SCHEMA),
        400: openapi.Response('Données invalides', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

ACTIVATE_EMAIL_SWAGGER = swagger_auto_schema(
    operation_summary="Confirmer l'adresse email",
    tags=['User - Auth'],
    request_body=ACTIVATE_EMAIL_REQUEST_SCHEMA,
    responses={
        200: openapi.Response('Email confirmé', SUCCESS_MESSAGE_SCHEMA),
        400: openapi.Response('Lien ou données invalides', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

RESEND_CONFIRMATION_SWAGGER = swagger_auto_schema(
    operation_summary="Renvoyer l'email de confirmation",
    tags=['User - Auth'],
    request_body=EMAIL_REQUEST_SCHEMA,
    responses={
        200: openapi.Response(
            'Email renvoyé',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'dev_activation_link': openapi.Schema(type=openapi.TYPE_STRING),
                    'dev_confirmation_link': openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
        400: openapi.Response('Données invalides', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

LOGIN_SWAGGER = swagger_auto_schema(
    operation_summary='Connexion utilisateur métier',
    tags=['User - Auth'],
    request_body=LOGIN_REQUEST_SCHEMA,
    responses={
        200: openapi.Response(
            'Connexion réussie',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': USER_SCHEMA,
                    'tokens': TOKEN_SCHEMA,
                },
            ),
        ),
        400: openapi.Response('Données invalides', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

REFRESH_SWAGGER = swagger_auto_schema(
    operation_summary='Rafraîchir le token utilisateur métier',
    tags=['User - Auth'],
    request_body=REFRESH_REQUEST_SCHEMA,
    responses={
        200: openapi.Response(
            'Token rafraîchi',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'tokens': TOKEN_SCHEMA,
                },
            ),
        ),
        400: openapi.Response('Refresh invalide', ERROR_SCHEMA),
        403: openapi.Response('Compte désactivé', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

LOGOUT_SWAGGER = swagger_auto_schema(
    operation_summary='Déconnexion utilisateur métier',
    tags=['User - Auth'],
    security=[{'Bearer': []}],
    request_body=REFRESH_REQUEST_SCHEMA,
    responses={
        200: openapi.Response('Déconnexion réussie', SUCCESS_MESSAGE_SCHEMA),
        400: openapi.Response('Refresh invalide', ERROR_SCHEMA),
        403: openapi.Response('Authentification requise', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

ME_SWAGGER = swagger_auto_schema(
    operation_summary='Récupérer mon compte utilisateur',
    tags=['User - Me'],
    security=[{'Bearer': []}],
    responses={
        200: openapi.Response('Compte utilisateur', USER_RESPONSE_SCHEMA),
        403: openapi.Response('Authentification requise', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

PROFILE_ME_SWAGGER = swagger_auto_schema(
    operation_summary='Récupérer mon profil utilisateur',
    tags=['User - Profile'],
    security=[{'Bearer': []}],
    responses={
        200: openapi.Response('Profil utilisateur', PROFILE_RESPONSE_SCHEMA),
        403: openapi.Response('Authentification requise', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

PROFILE_CREATE_SWAGGER = swagger_auto_schema(
    operation_summary='Créer ou compléter mon profil utilisateur',
    tags=['User - Profile'],
    security=[{'Bearer': []}],
    manual_parameters=PROFILE_MANUAL_PARAMETERS,
    consumes=['multipart/form-data'],
    responses={
        201: openapi.Response('Profil créé', PROFILE_MUTATION_RESPONSE_SCHEMA),
        200: openapi.Response(
            'Profil déjà existant et mis à jour',
            PROFILE_MUTATION_RESPONSE_SCHEMA,
        ),
        400: openapi.Response('Données invalides', ERROR_SCHEMA),
        403: openapi.Response('Authentification requise', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

PROFILE_UPDATE_SWAGGER = swagger_auto_schema(
    operation_summary='Mettre à jour mon profil utilisateur',
    tags=['User - Profile'],
    security=[{'Bearer': []}],
    manual_parameters=PROFILE_MANUAL_PARAMETERS,
    consumes=['multipart/form-data'],
    responses={
        200: openapi.Response('Profil mis à jour', PROFILE_MUTATION_RESPONSE_SCHEMA),
        400: openapi.Response('Données invalides', ERROR_SCHEMA),
        403: openapi.Response('Authentification requise', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

PROFILE_DELETE_SWAGGER = swagger_auto_schema(
    operation_summary='Supprimer mon profil utilisateur',
    tags=['User - Profile'],
    security=[{'Bearer': []}],
    responses={
        200: openapi.Response('Profil supprimé', SUCCESS_MESSAGE_SCHEMA),
        403: openapi.Response('Authentification requise', ERROR_SCHEMA),
        404: openapi.Response('Profil introuvable', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

CHANGE_PASSWORD_SWAGGER = swagger_auto_schema(
    operation_summary='Changer mon mot de passe utilisateur',
    tags=['User - Me'],
    security=[{'Bearer': []}],
    request_body=CHANGE_PASSWORD_REQUEST_SCHEMA,
    responses={
        200: openapi.Response('Mot de passe modifié', SUCCESS_MESSAGE_SCHEMA),
        400: openapi.Response('Données invalides', ERROR_SCHEMA),
        403: openapi.Response('Authentification requise', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)
