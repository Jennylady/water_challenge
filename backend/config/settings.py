from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta
from helpers.utils import get_server_settings
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
IP_ADDR, PORT = get_server_settings()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', os.getenv('BACKEND_HOST', '')]
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'

LOCAL_APPS = [
    'apps.accounts.admin.apps.AccountsAdminConfig',
    'apps.accounts.user.apps.AccountsUserConfig',
    'apps.formation.apps.FormationConfig',
    'apps.challenges.apps.ChallengesConfig',
    # 'apps.communaute.apps.CommunauteConfig',
    'apps.recompenses.apps.RecompensesConfig',
    'apps.notifications.apps.NotificationsConfig',
]

THIRD_APPS = [
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'django_extensions',
]

INSTALLED_APPS = [
    *LOCAL_APPS,
    *THIRD_APPS,
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

database_engine = os.getenv('DATABASE_ENGINE', 'sqlite').lower()
if database_engine == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': os.getenv('DATABASE_USER'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD'),
            'HOST': os.getenv('DATABASE_HOST'),
            'PORT': os.getenv('DATABASE_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'ssl': {'disabled': True},
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DATABASE_NAME', 'db.sqlite3'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Entrez le token JWT au format "Bearer <token>"',
        }
    },
    'USE_SESSION_AUTH': False,
    'DEFAULT_API_URL': os.getenv('BACKEND_DOMAIN', f'http://{IP_ADDR}:{PORT}'),
}

LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Indian/Antananarivo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'statics')]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

HANDLER404 = 'config.views.custom_404'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
BASE_URL = os.getenv('BASE_URL', f'http://{IP_ADDR}:{PORT}')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

AUTH_USER_MODEL = 'accounts_admin.AdminUser'
AUTHENTICATION_BACKENDS = ['apps.accounts.admin.backends.AdminEmailBackend']

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=int(os.getenv('ACCESS_TOKEN_DAYS', '5'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('REFRESH_TOKEN_DAYS', '30'))),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_PRIVATE_NETWORK = True
CSRF_TRUSTED_ORIGINS = ['http://*', 'https://*']

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '465'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f'Water Ambassador <{EMAIL_HOST_USER}>')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ACCOUNT_ACTIVATION_EXPIRES_IN_MINUTES = int(
    os.getenv('ACCOUNT_ACTIVATION_EXPIRES_IN_MINUTES', '1440')
)
ACCOUNT_ACTIVATION_CLOCK_SKEW_SECONDS = 30
ACCOUNT_ACTIVATION_ISSUER = 'water-ambassadors-api'
ACCOUNT_ACTIVATION_AUDIENCE = 'water-ambassadors-email-activation'

ACCOUNT_ACTIVATION_SIGNING_KEY = os.getenv("ACCOUNT_ACTIVATION_SIGNING_KEY")
ACCOUNT_ACTIVATION_ENCRYPTION_SECRET = os.getenv("ACCOUNT_ACTIVATION_ENCRYPTION_SECRET")

CHALLENGES_NOTIFICATION_HANDLER = 'apps.notifications.services.notification_challenge_handler'
CHALLENGES_REWARD_HANDLER = 'apps.recompenses.services.reward_challenge_handler'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}