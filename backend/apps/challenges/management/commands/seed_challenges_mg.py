import secrets
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.accounts.user.models import User
from apps.challenges.models import Defi, DefiUtilisateur
from apps.formation.models import Module
from apps.notifications.models import Notification
from apps.notifications.services import notifier


def _challenge_cover_files():
    """Lit dynamiquement les couvertures réellement présentes dans MEDIA_ROOT."""
    directory = Path(settings.MEDIA_ROOT) / "challenges/defis/couvertures"
    if not directory.is_dir():
        return []

    allowed = {".jpg", ".jpeg", ".png", ".webp"}
    return sorted(
        path.relative_to(settings.MEDIA_ROOT).as_posix()
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in allowed
    )


def _random_cover(files):
    return secrets.choice(files) if files else None


CHALLENGES = {
    "ny-rano-sy-ny-maha-zava-dehibe-azy": [
        ("Manara-maso ny fandaniana rano ao an-trano", "Soraty mandritra ny telo andro ny rano ampiasaina ao an-trano."),
        ("Mampianatra ankizy dimy momba ny fitsitsiana rano", "Manaova fanentanana fohy ho an'ny ankizy dimy farafahakeliny."),
        ("Manadio toerana manodidina loharano iray", "Mandamina fanadiovana kely manodidina loharano na paompy."),
    ],
    "fisorohana-ny-fandotoana-ny-rano": [
        ("Mikarakara fanadiovana manodidina tatatra", "Manadio tatatra iray miaraka amin'ny olona ao an-toerana."),
        ("Mamorona afisy momba ny rano madio", "Mamorona afisy amin'ny teny malagasy momba ny fiarovana ny rano."),
        ("Manangona sy manasokajy fako plastika", "Angony sy saraho araka ny sokajiny ny fako plastika."),
    ],
    "fitsitsiana-rano-ao-an-tokantrano": [
        ("Mitady sy manamboatra fivoahan-drano", "Fantaro ny toerana misy fivoahan-drano ary amboary na ampandreneso ny tompon'andraikitra."),
        ("Manao tabilao fitsitsiana rano", "Mamorona tabilao tsotra hanaraha-maso ny fandaniana rano isan'andro."),
        ("Mampiasa ranonorana amin'ny asa iray", "Angony ny ranonorana ary ampiasao amin'ny fanondrahana na fanadiovana."),
    ],
    "ny-andraikitry-ny-mpandrindra-rano": [
        ("Mitarika fivoriana fanentanana fohy", "Mitarika fivoriana 15 minitra momba ny fiarovana ny rano."),
        ("Manomana drafitra hetsika fiarovana rano", "Mamorona drafitra ahitana tanjona, asa, daty ary tompon'andraikitra."),
        ("Manao tatitra misy porofo", "Mamorona tatitra misy toerana, daty, vokatra ary porofo amin'ny hetsika iray."),
    ],
}


class Command(BaseCommand):
    help = "Mamorona défis maro mifandray amin'ny modules ary manomana azy ho an'ny moderators."

    @transaction.atomic
    def handle(self, *args, **options):
        if not Module.objects.exists():
            raise CommandError("Alefaso aloha: python manage.py seed_formations_mg")

        moderators = User.objects.filter(
            role=User.Role.MODERATOR,
            is_active=True,
            is_email_verified=True,
        )
        cover_files = _challenge_cover_files()

        global_order = 1
        for module_slug, challenge_list in CHALLENGES.items():
            module = Module.objects.filter(slug=module_slug).first()
            if module is None:
                self.stdout.write(self.style.WARNING(f"Module tsy hita: {module_slug}"))
                continue

            for local_order, (title, description) in enumerate(challenge_list, start=1):
                challenge, created = Defi.objects.update_or_create(
                    module=module,
                    titre=title,
                    defaults={
                        "description": description,
                        "resultat_attendu": "Hetsika vita sy porofo mazava.",
                        "criteres_validation": "Tatitra mazava, toerana, daty ary sary porofo.",
                        "niveau": slugify(module.niveau).replace("-", "_") if module.niveau else Defi.Niveau.DEBUTANT,
                        "ordre": global_order,
                        "duree_estimee": "1 andro",
                        "points_recompense": 25,
                        "nombre_photos_min": 1,
                        "nombre_photos_max": 5,
                        "video_obligatoire": False,
                        "image_couverture": _random_cover(cover_files),
                        "est_obligatoire": local_order <= 2,
                        "est_actif": True,
                        "est_publie": True,
                        "est_ouvert": True,
                    },
                )
                global_order += 1

                for user in moderators:
                    state, state_created = DefiUtilisateur.objects.get_or_create(
                        utilisateur=user,
                        defi=challenge,
                        defaults={"statut": DefiUtilisateur.Statut.VERROUILLE},
                    )
                    if created and state_created:
                        notifier(
                            user,
                            Notification.Type.AUTRE,
                            "Misy défi vaovao",
                            f"Nampidirina ny défi « {challenge.titre} » ao amin'ny module « {module.titre} ».",
                            f"/challenges/defis/{challenge.id}/",
                        )

        self.stdout.write(self.style.SUCCESS("Challenges seedés avec succès."))