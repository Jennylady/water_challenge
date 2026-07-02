from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token


def send_email_confirmation(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    frontend_url = settings.FRONTEND_URL.rstrip("/")
    confirmation_link = f"{frontend_url}/confirm-email/{uid}/{token}"

    subject = "Confirmez votre compte Water Ambassador"

    message = f"""
Bonjour {user.first_name},

Merci pour votre inscription sur Water Ambassador.

Pour activer votre compte, cliquez sur le lien suivant :

{confirmation_link}

Si vous n'êtes pas à l'origine de cette inscription, ignorez simplement cet email.

Water Ambassador
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return confirmation_link