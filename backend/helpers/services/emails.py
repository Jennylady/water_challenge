from datetime import datetime
from dotenv import load_dotenv
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging
import os
import traceback

load_dotenv()
LOGGER = logging.getLogger(__name__)

TEMPLATES_EMAIL = {
    'account_activation': 'emails/account_activation.html',
    'otp_verification': 'emails/otp_verification.html',
    'reset_password': 'emails/reset_password.html',
    'support_message': 'emails/support_message.html',
    'moderateur_invitation': 'emails/moderateur_invitation.html',
}


def envoyer_email(list_email_to_send: list, template_name: str, data: dict):
    try:
        data = data or {}
        data['current_year'] = datetime.now().year
        data['logo_url'] = os.getenv('LOGO_URL', '')
        data['site_url'] = os.getenv('SITE_URL', '')
        data['support_email'] = os.getenv('SUPPORT_EMAIL', '')

        objet = data.get('subject', "Water Challenge")
        html_message = render_to_string(TEMPLATES_EMAIL[template_name], data)
        email_config = settings.DEFAULT_FROM_EMAIL

        send_mail(
            objet,
            '',
            email_config,
            list_email_to_send,
            html_message=html_message,
            fail_silently=False,
        )
        LOGGER.info('Email envoyé avec succès.')
        return True
    except Exception as e:
        print(f"Erreur lors d'envoi de l'email: {e}")
        print(traceback.format_exc())
        LOGGER.error(f"Erreur lors d'envoi de l'email: {e}")
        return False
