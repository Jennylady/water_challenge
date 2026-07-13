import os
import sys
from datetime import datetime, timedelta
from base64 import b64decode, b64encode

import jwt
from dotenv import load_dotenv
from django.conf import settings
from django.utils import timezone as django_timezone
from rest_framework.request import Request
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

try:
    from cryptography.fernet import Fernet, InvalidToken as FernetInvalidToken
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
except Exception:
    Cipher = algorithms = modes = default_backend = None
    Fernet = FernetInvalidToken = hashes = HKDF = None

load_dotenv()


def _derive_fernet_key(secret: str, context: str) -> bytes:
    """Dérive une clé Fernet indépendante à partir d'un secret et d'un contexte."""
    if Fernet is None or HKDF is None or hashes is None:
        raise RuntimeError('cryptography is not installed')
    if not isinstance(secret, str) or len(secret) < 32:
        raise ValueError('Le secret de chiffrement doit contenir au moins 32 caractères.')
    if not isinstance(context, str) or not context:
        raise ValueError('Le contexte de chiffrement est requis.')

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'water-ambassadors-secure-token-v1',
        info=context.encode('utf-8'),
    )
    raw_key = hkdf.derive(secret.encode('utf-8'))
    return b64encode(raw_key).replace(b'+', b'-').replace(b'/', b'_')


def encrypt_authenticated(plaintext: str, *, secret: str, context: str) -> str:
    """Chiffrement authentifié et URL-safe avec IV aléatoire et contrôle d'intégrité."""
    if not isinstance(plaintext, str):
        raise TypeError('plaintext doit être une chaîne de caractères.')
    fernet = Fernet(_derive_fernet_key(secret, context))
    return fernet.encrypt(plaintext.encode('utf-8')).decode('ascii')


def decrypt_authenticated(token: str, *, secret: str, context: str, ttl: int | None = None) -> str:
    """Déchiffre un token Fernet et rejette toute altération."""
    if not isinstance(token, str) or not token.strip():
        raise ValueError('Token chiffré invalide.')
    fernet = Fernet(_derive_fernet_key(secret, context))
    try:
        value = fernet.decrypt(token.strip().encode('ascii'), ttl=ttl)
    except (FernetInvalidToken, ValueError, UnicodeError) as exc:
        raise ValueError('Token chiffré invalide ou expiré.') from exc
    return value.decode('utf-8')


def get_server_settings():
    ip_addr = '127.0.0.1'
    port = 8000
    if 'runserver' in sys.argv:
        runserver_index = sys.argv.index('runserver')
        if len(sys.argv) > runserver_index + 1:
            ip_port = sys.argv[runserver_index + 1]
            if ':' in ip_port:
                ip_addr, port = ip_port.split(':')
            else:
                port = ip_port
    return ip_addr, int(port)


def get_token_from_request(request: Request) -> str | None:
    authorization_header = request.headers.get('Authorization')
    if authorization_header and authorization_header.startswith('Bearer '):
        return authorization_header.split()[1]
    return None


def get_timezone():
    tz = os.getenv('TIMEZONE_HOURS', '3')
    if '-' in tz:
        return django_timezone.now() - timedelta(hours=int(tz.strip()[1:]))
    return django_timezone.now() + timedelta(hours=int(tz))


def enc_dec(plaintext, type='e'):
    if Cipher is None:
        raise RuntimeError('cryptography is not installed')

    cipher = Cipher(
        algorithms.AES(os.getenv('AES_KEY', '0123456789abcdef').encode()),
        modes.CFB(os.getenv('AES_IV', 'abcdef0123456789').encode()),
        backend=default_backend(),
    )
    if type == 'e':
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        return b64encode(ciphertext).decode()
    if type == 'd':
        decryptor = cipher.decryptor()
        ciphertext = b64decode(plaintext)
        decrypted_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_plaintext.decode()
    return 'type de cryptage inconnu'


def generate_jwt_token(payload: dict, expires_in_minutes: int = 1440) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    payload.update({'exp': expiration})
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.SIMPLE_JWT['ALGORITHM'])
    return token


def decode_jwt_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT['ALGORITHM']])


def get_user(token):
    try:
        from apps.accounts.user.models import User, UserOutstandingToken

        access_token = AccessToken(token)
        if access_token.get('account_type') != 'user':
            return None

        jti = access_token.get('jti')
        user_id = access_token.get('app_user_id')
        if not jti or not user_id:
            return None
        if UserOutstandingToken.objects.filter(jti=jti, blacklisted=True).exists():
            return None

        return User.objects.get(id=user_id)
    except (TokenError, Exception):
        return None


def get_admin(token):
    try:
        from apps.accounts.admin.models import AdminUser

        access_token = AccessToken(token)
        admin_id = access_token.get('user_id')
        if not admin_id:
            return None
        return AdminUser.objects.get(id=admin_id)
    except (TokenError, Exception):
        return None


def temps_ecoule(timestamp1, timestamp2):
    if isinstance(timestamp1, (int, float)):
        timestamp1 = datetime.fromtimestamp(timestamp1)
    if isinstance(timestamp2, (int, float)):
        timestamp2 = datetime.fromtimestamp(timestamp2)

    delta = abs(timestamp1 - timestamp2)

    if delta.total_seconds() < 1:
        return 'maintenant'

    secondes = int(delta.total_seconds())
    minutes = secondes // 60
    heures = minutes // 60
    jours = delta.days
    mois = jours // 30
    annees = jours // 365

    if annees > 0:
        return f'il y a {annees} an{"s" if annees > 1 else ""}'
    if mois > 0:
        return f'il y a {mois} mois'
    if jours > 0:
        return f'il y a {jours} jour{"s" if jours > 1 else ""}'
    if heures > 0:
        return f'il y a {heures} heure{"s" if heures > 1 else ""}'
    if minutes > 0:
        return f'il y a {minutes} minute{"s" if minutes > 1 else ""}'
    return f'il y a {secondes} seconde{"s" if secondes > 1 else ""}'