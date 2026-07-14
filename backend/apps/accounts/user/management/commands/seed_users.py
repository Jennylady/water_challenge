from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.admin.models import AdminUser
from apps.accounts.user.models import Profile, User
from apps.notifications.models import Notification
from apps.notifications.services import notifier


SUPERADMIN = {
    "email": "raph@gmail.com",
    "password": "hpar",
    "first_name": "Raph",
    "last_name": "Administrateur",
}

MODERATORS = [
    {
        "email": "jennysc@gmail.com",
        "password": "Love2022.",
        "first_name": "Jenny",
        "last_name": "SC",
        "faritra": "Analamanga",
    },
    {
        "email": "moderateur@water.mg",
        "password": "Moderator@2026",
        "first_name": "Miora",
        "last_name": "Rano",
        "faritra": "Boeny",
    },
    {
        "email": "fano@water.mg",
        "password": "Water@2026",
        "first_name": "Fano",
        "last_name": "Rakoto",
        "faritra": "Haute Matsiatra",
    },
    {
        "email": "saholy@water.mg",
        "password": "Water@2026",
        "first_name": "Saholy",
        "last_name": "Razanaka",
        "faritra": "Atsinanana",
    },
]


class Command(BaseCommand):
    help = "Crée le super administrateur local et les comptes modérateurs de démonstration."

    @transaction.atomic
    def handle(self, *args, **options):
        admin, _ = AdminUser.objects.get_or_create(
            email=SUPERADMIN["email"],
            defaults={
                "first_name": SUPERADMIN["first_name"],
                "last_name": SUPERADMIN["last_name"],
                "role": AdminUser.Role.SUPERADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        admin.first_name = SUPERADMIN["first_name"]
        admin.last_name = SUPERADMIN["last_name"]
        admin.role = AdminUser.Role.SUPERADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.set_password(SUPERADMIN["password"])
        admin.save()

        for item in MODERATORS:
            user, _ = User.objects.get_or_create(
                email=item["email"],
                defaults={
                    "first_name": item["first_name"],
                    "last_name": item["last_name"],
                    "role": User.Role.MODERATOR,
                    "is_active": True,
                    "is_email_verified": True,
                },
            )
            user.first_name = item["first_name"]
            user.last_name = item["last_name"]
            user.role = User.Role.MODERATOR
            user.is_active = True
            user.is_email_verified = True
            user.set_password(item["password"])
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.faritra = item["faritra"]
            profile.save(update_fields=["faritra"])

            if not Notification.objects.filter(
                destinataire=user,
                type=Notification.Type.AUTRE,
                titre="Tongasoa eto amin'ny Water Challenge",
            ).exists():
                notifier(
                    user,
                    Notification.Type.AUTRE,
                    "Tongasoa eto amin'ny Water Challenge",
                    "Voamarina sy mavitrika ny kaontinao mpandrindra. Afaka manomboka ny fiofanana ianao.",
                    "/formation/modules/",
                )

        self.stdout.write(self.style.SUCCESS("Comptes seedés avec succès."))
        self.stdout.write("Superuser local : raph@gmail.com / hpar")
        self.stdout.write("Utilisateur demandé : jennysc@gmail.com / Love2022.")
