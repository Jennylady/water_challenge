import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.db import transaction

from helpers.helper import decrypt_authenticated, encrypt_authenticated
from helpers.services.emails import envoyer_email

from .models import User


ACTIVATION_PURPOSE = 'user_email_activation'
ACTIVATION_ACCOUNT_TYPE = 'user'
ACTIVATION_TOKEN_VERSION = 1
ACTIVATION_ISSUER = getattr(settings, 'ACCOUNT_ACTIVATION_ISSUER', 'water-ambassadors-api')
ACTIVATION_AUDIENCE = getattr(
    settings, 'ACCOUNT_ACTIVATION_AUDIENCE', 'water-ambassadors-email-activation'
)
ACTIVATION_EXPIRES_IN_MINUTES = int(
    getattr(settings, 'ACCOUNT_ACTIVATION_EXPIRES_IN_MINUTES', 60 * 24)
)
ACTIVATION_CLOCK_SKEW_SECONDS = int(
    getattr(settings, 'ACCOUNT_ACTIVATION_CLOCK_SKEW_SECONDS', 30)
)
ACTIVATION_JWT_ALGORITHM = 'HS256'

_INNER_CONTEXT = 'water-ambassadors:activation:encrypted-payload:v1'
_OUTER_CONTEXT = 'water-ambassadors:activation:encrypted-jwt:v1'


class ActivationTokenError(ValueError):
    """Erreur publique volontairement générique pour ne pas divulguer les détails du compte."""


def _signing_key() -> str:
    key = getattr(settings, 'ACCOUNT_ACTIVATION_SIGNING_KEY', settings.SECRET_KEY)
    if not isinstance(key, str) or len(key) < 32:
        raise RuntimeError('ACCOUNT_ACTIVATION_SIGNING_KEY doit contenir au moins 32 caractères.')
    return key


def _encryption_secret() -> str:
    secret = getattr(settings, 'ACCOUNT_ACTIVATION_ENCRYPTION_SECRET', settings.SECRET_KEY)
    if not isinstance(secret, str) or len(secret) < 32:
        raise RuntimeError(
            'ACCOUNT_ACTIVATION_ENCRYPTION_SECRET doit contenir au moins 32 caractères.'
        )
    return secret


def _normaliser_email(email: str) -> str:
    return (email or '').strip().lower()


def _build_encrypted_payload(user: User, activation_nonce=None) -> str:
    nonce = activation_nonce or user.email_activation_nonce
    payload = {
        'version': ACTIVATION_TOKEN_VERSION,
        'purpose': ACTIVATION_PURPOSE,
        'account_type': ACTIVATION_ACCOUNT_TYPE,
        'user_id': str(user.pk),
        'email': _normaliser_email(user.email),
        'activation_nonce': str(nonce),
        'role': str(user.role),
    }
    serialized = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    return encrypt_authenticated(
        serialized, secret=_encryption_secret(), context=_INNER_CONTEXT
    )


def generate_account_activation_token(user: User, activation_nonce=None) -> str:
    """
    1) chiffre la payload métier ;
    2) place cette payload dans un JWT signé et expirant ;
    3) rechiffre entièrement le JWT avant son envoi.
    """
    now = datetime.now(timezone.utc)
    encrypted_payload = _build_encrypted_payload(user, activation_nonce=activation_nonce)
    jwt_payload = {
        'typ': 'email_activation',
        'sub': 'email_activation',
        'data': encrypted_payload,
        'jti': uuid.uuid4().hex,
        'iat': now,
        'nbf': now,
        'exp': now + timedelta(minutes=ACTIVATION_EXPIRES_IN_MINUTES),
        'iss': ACTIVATION_ISSUER,
        'aud': ACTIVATION_AUDIENCE,
    }
    signed_token = jwt.encode(
        jwt_payload, _signing_key(), algorithm=ACTIVATION_JWT_ALGORITHM
    )
    return encrypt_authenticated(
        signed_token, secret=_encryption_secret(), context=_OUTER_CONTEXT
    )


def decode_account_activation_token(token: str) -> dict:
    try:
        signed_token = decrypt_authenticated(
            token, secret=_encryption_secret(), context=_OUTER_CONTEXT
        )
        envelope = jwt.decode(
            signed_token,
            _signing_key(),
            algorithms=[ACTIVATION_JWT_ALGORITHM],
            audience=ACTIVATION_AUDIENCE,
            issuer=ACTIVATION_ISSUER,
            leeway=ACTIVATION_CLOCK_SKEW_SECONDS,
            options={
                'require': ['typ', 'sub', 'data', 'jti', 'iat', 'nbf', 'exp', 'iss', 'aud']
            },
        )
        if envelope.get('typ') != 'email_activation' or envelope.get('sub') != 'email_activation':
            raise ActivationTokenError('Lien de confirmation invalide ou expiré.')

        encrypted_payload = envelope.get('data')
        decrypted_json = decrypt_authenticated(
            encrypted_payload, secret=_encryption_secret(), context=_INNER_CONTEXT
        )
        payload = json.loads(decrypted_json)
    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
        UnicodeError,
    ) as exc:
        raise ActivationTokenError('Lien de confirmation invalide ou expiré.') from exc

    required = {
        'version', 'purpose', 'account_type', 'user_id', 'email', 'activation_nonce', 'role'
    }
    if not isinstance(payload, dict) or not required.issubset(payload):
        raise ActivationTokenError('Lien de confirmation invalide ou expiré.')
    if payload.get('version') != ACTIVATION_TOKEN_VERSION:
        raise ActivationTokenError('Version du lien de confirmation non prise en charge.')
    if payload.get('purpose') != ACTIVATION_PURPOSE:
        raise ActivationTokenError('Lien de confirmation invalide ou expiré.')
    if payload.get('account_type') != ACTIVATION_ACCOUNT_TYPE:
        raise ActivationTokenError('Ce lien ne correspond pas à un compte utilisateur.')

    user_id = str(payload.get('user_id', ''))
    if not user_id.isdigit():
        raise ActivationTokenError('Lien de confirmation invalide ou expiré.')
    try:
        uuid.UUID(str(payload.get('activation_nonce', '')))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ActivationTokenError('Lien de confirmation invalide ou expiré.') from exc
    if not _normaliser_email(payload.get('email')):
        raise ActivationTokenError('Lien de confirmation invalide ou expiré.')
    return payload


def _get_user_from_activation_payload(payload: dict, *, for_update=False) -> User:
    queryset = User.objects
    if for_update:
        queryset = queryset.select_for_update()
    try:
        user = queryset.get(pk=int(payload['user_id']))
    except (User.DoesNotExist, ValueError, TypeError) as exc:
        raise ActivationTokenError('Lien de confirmation invalide ou expiré.') from exc

    email_matches = secrets.compare_digest(
        _normaliser_email(user.email).encode('utf-8'),
        _normaliser_email(payload.get('email')).encode('utf-8'),
    )
    nonce_matches = secrets.compare_digest(
        str(user.email_activation_nonce).encode('ascii'),
        str(payload.get('activation_nonce')).encode('ascii'),
    )
    role_matches = secrets.compare_digest(
        str(user.role).encode('utf-8'), str(payload.get('role', '')).encode('utf-8')
    )
    if not email_matches or not nonce_matches or not role_matches or not user.is_active:
        raise ActivationTokenError('Lien de confirmation invalide ou expiré.')
    return user


@transaction.atomic
def activate_account_email(token: str):
    payload = decode_account_activation_token(token)
    user = _get_user_from_activation_payload(payload, for_update=True)

    if user.is_email_verified:
        user.email_activation_nonce = uuid.uuid4()
        user.save(update_fields=['email_activation_nonce', 'updated_at'])
        return user, False

    user.is_email_verified = True
    # Invalidation immédiate et définitive du token après son utilisation.
    user.email_activation_nonce = uuid.uuid4()
    user.save(update_fields=['is_email_verified', 'email_activation_nonce', 'updated_at'])
    return user, True


def send_account_activation_email(user: User, *, rotate_nonce=False):
    if user.is_email_verified:
        raise ValueError('Cette adresse email est déjà confirmée.')

    previous_nonce = user.email_activation_nonce
    if rotate_nonce:
        # Tout ancien lien devient invalide dès qu'un nouveau lien est demandé.
        user.email_activation_nonce = uuid.uuid4()
        user.save(update_fields=['email_activation_nonce', 'updated_at'])

    activation_token = generate_account_activation_token(user)
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    activation_link = f'{frontend_url}/confirm-email/{activation_token}'

    data = {
        'subject': 'Confirmez votre compte Water Ambassador',
        'first_name': user.first_name,
        'account_type': ACTIVATION_ACCOUNT_TYPE,
        'activation_link': activation_link,
        'email': user.email,
        'expires_in_minutes': ACTIVATION_EXPIRES_IN_MINUTES,
    }
    try:
        envoyer_email([user.email], 'account_activation', data)
    except Exception:
        if rotate_nonce:
            User.objects.filter(
                pk=user.pk, email_activation_nonce=user.email_activation_nonce
            ).update(email_activation_nonce=previous_nonce)
            user.email_activation_nonce = previous_nonce
        raise
    return activation_link
