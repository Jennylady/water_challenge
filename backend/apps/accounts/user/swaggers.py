from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


ERROR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
        'message': openapi.Schema(type=openapi.TYPE_STRING, example='Données invalides.'),
        'errors': openapi.Schema(type=openapi.TYPE_OBJECT),
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
        'avatar': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'scout_type': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'section': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'sampana': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'position': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'fivondronana': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'faritra': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'diosezy': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'level': openapi.Schema(type=openapi.TYPE_STRING),
        'points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'progression': openapi.Schema(type=openapi.TYPE_INTEGER),
        'current_badge': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'bio': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
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
        'phone': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'birth_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, nullable=True),
        'role': openapi.Schema(type=openapi.TYPE_STRING),
        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'profile': PROFILE_SCHEMA,
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    },
)

REGISTER_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'first_name', 'last_name', 'password', 'password_confirm'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, example='user@example.com'),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='Toky'),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='Nandrasana'),
        'phone': openapi.Schema(type=openapi.TYPE_STRING, example='+261340000000'),
        'birth_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, example='2000-01-01'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, example='StrongPass123'),
        'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, example='StrongPass123'),
        'scout_type': openapi.Schema(type=openapi.TYPE_STRING, example='fanilon'),
        'section': openapi.Schema(type=openapi.TYPE_STRING, example='mavo'),
        'sampana': openapi.Schema(type=openapi.TYPE_STRING, example='Sampana test'),
        'position': openapi.Schema(type=openapi.TYPE_STRING, example='beazina'),
        'fivondronana': openapi.Schema(type=openapi.TYPE_STRING, example='Antananarivo'),
        'faritra': openapi.Schema(type=openapi.TYPE_STRING, example='Analamanga'),
        'diosezy': openapi.Schema(type=openapi.TYPE_STRING, example='Antananarivo'),
    },
)

LOGIN_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

EMAIL_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
    },
)

REFRESH_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['refresh'],
    properties={
        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

CHANGE_PASSWORD_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['old_password', 'new_password', 'new_password_confirm'],
    properties={
        'old_password': openapi.Schema(type=openapi.TYPE_STRING),
        'new_password': openapi.Schema(type=openapi.TYPE_STRING),
        'new_password_confirm': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

PROFILE_MANUAL_PARAMETERS = [
    openapi.Parameter('avatar', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False, description='Photo de profil'),
    openapi.Parameter('first_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Prénom'),
    openapi.Parameter('last_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Nom'),
    openapi.Parameter('phone', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Téléphone'),
    openapi.Parameter('birth_date', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Date de naissance YYYY-MM-DD'),
    openapi.Parameter('scout_type', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Type scout'),
    openapi.Parameter('section', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Section'),
    openapi.Parameter('sampana', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Sampana'),
    openapi.Parameter('position', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Position'),
    openapi.Parameter('fivondronana', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Fivondronana'),
    openapi.Parameter('faritra', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Faritra'),
    openapi.Parameter('diosezy', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Diosezy'),
    openapi.Parameter('bio', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Biographie'),
]

REGISTER_SWAGGER = swagger_auto_schema(
    operation_summary='Créer un compte utilisateur métier',
    operation_description='Inscription d’un ambassadeur avec création du profil initial et envoi de l’email de confirmation.',
    tags=['User - Auth'],
    request_body=REGISTER_REQUEST_SCHEMA,
    responses={
        201: openapi.Response('Compte créé', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'user': USER_SCHEMA,
                'dev_activation_link': openapi.Schema(type=openapi.TYPE_STRING),
                'dev_confirmation_link': openapi.Schema(type=openapi.TYPE_STRING),
            },
        )),
        400: openapi.Response('Erreur validation', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

ACTIVATE_EMAIL_SWAGGER = swagger_auto_schema(
    operation_summary='Confirmer l’email utilisateur',
    operation_description='Active le compte utilisateur à partir du uidb64 et du token envoyés par email.',
    tags=['User - Auth'],
    responses={
        200: openapi.Response('Email confirmé', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
            },
        )),
        400: openapi.Response('Lien invalide', ERROR_SCHEMA),
    },
)

RESEND_CONFIRMATION_SWAGGER = swagger_auto_schema(
    operation_summary='Renvoyer l’email de confirmation',
    tags=['User - Auth'],
    request_body=EMAIL_REQUEST_SCHEMA,
    responses={
        200: openapi.Response('Email renvoyé'),
        400: openapi.Response('Erreur validation', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

LOGIN_SWAGGER = swagger_auto_schema(
    operation_summary='Connexion utilisateur métier',
    tags=['User - Auth'],
    request_body=LOGIN_REQUEST_SCHEMA,
    responses={
        200: openapi.Response('Connexion réussie', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'user': USER_SCHEMA,
                'tokens': TOKEN_SCHEMA,
            },
        )),
        400: openapi.Response('Erreur validation', ERROR_SCHEMA),
        500: openapi.Response('Erreur serveur', ERROR_SCHEMA),
    },
)

REFRESH_SWAGGER = swagger_auto_schema(
    operation_summary='Rafraîchir le token utilisateur métier',
    tags=['User - Auth'],
    request_body=REFRESH_REQUEST_SCHEMA,
    responses={
        200: openapi.Response('Token rafraîchi'),
        400: openapi.Response('Refresh invalide', ERROR_SCHEMA),
        403: openapi.Response('Compte désactivé', ERROR_SCHEMA),
    },
)

LOGOUT_SWAGGER = swagger_auto_schema(
    operation_summary='Déconnexion utilisateur métier',
    tags=['User - Auth'],
    security=[{'Bearer': []}],
    request_body=REFRESH_REQUEST_SCHEMA,
    responses={
        200: openapi.Response('Déconnexion réussie'),
        400: openapi.Response('Refresh invalide', ERROR_SCHEMA),
    },
)

ME_SWAGGER = swagger_auto_schema(
    operation_summary='Récupérer mon compte utilisateur',
    tags=['User - Me'],
    security=[{'Bearer': []}],
    responses={
        200: openapi.Response('Compte utilisateur', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'user': USER_SCHEMA,
            },
        )),
        401: openapi.Response('Non authentifié', ERROR_SCHEMA),
    },
)

PROFILE_ME_SWAGGER = swagger_auto_schema(
    operation_summary='Récupérer mon profil utilisateur',
    tags=['User - Profile'],
    security=[{'Bearer': []}],
    responses={
        200: openapi.Response('Profil utilisateur', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'user': USER_SCHEMA,
                'profile': PROFILE_SCHEMA,
            },
        )),
        401: openapi.Response('Non authentifié', ERROR_SCHEMA),
    },
)

PROFILE_CREATE_SWAGGER = swagger_auto_schema(
    operation_summary='Créer ou compléter mon profil utilisateur',
    operation_description='Endpoint multipart. Utilise manual_parameters uniquement, sans request_body.',
    tags=['User - Profile'],
    security=[{'Bearer': []}],
    manual_parameters=PROFILE_MANUAL_PARAMETERS,
    consumes=['multipart/form-data'],
    responses={
        201: openapi.Response('Profil créé'),
        200: openapi.Response('Profil déjà existant, mis à jour'),
        400: openapi.Response('Erreur validation', ERROR_SCHEMA),
    },
)

PROFILE_UPDATE_SWAGGER = swagger_auto_schema(
    operation_summary='Mettre à jour mon profil utilisateur',
    operation_description='Endpoint multipart. Utilise manual_parameters uniquement, sans request_body.',
    tags=['User - Profile'],
    security=[{'Bearer': []}],
    manual_parameters=PROFILE_MANUAL_PARAMETERS,
    consumes=['multipart/form-data'],
    responses={
        200: openapi.Response('Profil mis à jour'),
        400: openapi.Response('Erreur validation', ERROR_SCHEMA),
        401: openapi.Response('Non authentifié', ERROR_SCHEMA),
    },
)

PROFILE_DELETE_SWAGGER = swagger_auto_schema(
    operation_summary='Supprimer mon profil utilisateur',
    tags=['User - Profile'],
    security=[{'Bearer': []}],
    responses={
        200: openapi.Response('Profil supprimé'),
        404: openapi.Response('Profil introuvable', ERROR_SCHEMA),
        401: openapi.Response('Non authentifié', ERROR_SCHEMA),
    },
)

CHANGE_PASSWORD_SWAGGER = swagger_auto_schema(
    operation_summary='Changer mon mot de passe utilisateur',
    tags=['User - Me'],
    security=[{'Bearer': []}],
    request_body=CHANGE_PASSWORD_REQUEST_SCHEMA,
    responses={
        200: openapi.Response('Mot de passe modifié'),
        400: openapi.Response('Erreur validation', ERROR_SCHEMA),
    },
)
