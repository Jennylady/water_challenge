from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from helpers.services.emails import envoyer_email
from .tokens import account_activation_token


def send_account_activation_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    activation_link = f'{frontend_url}/confirm-email/{uid}/{token}'

    data = {
        'subject': 'Confirmez votre compte Water Ambassador',
        'first_name': user.first_name,
        'activation_link': activation_link,
        'email': user.email,
    }
    envoyer_email([user.email], 'account_activation', data)
    return activation_link
