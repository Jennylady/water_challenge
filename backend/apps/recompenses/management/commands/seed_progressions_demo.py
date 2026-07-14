import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.user.models import Profile, User
from apps.challenges.models import Defi, DefiUtilisateur
from apps.formation.models import Module, ProgressionModule, TentativeQuiz
from apps.notifications.models import Notification
from apps.notifications.services import notifier
from apps.recompenses.models import BadgeUtilisateur, Certificat, ConfigurationNiveau
from apps.recompenses.services import synchroniser_progression_module


DEMO_EMAILS = [
    "jennysc@gmail.com",
    "moderateur@water.mg",
    "fano@water.mg",
    "saholy@water.mg",
]

# Chaque scénario produit une progression différente.
# quiz peut valoir: "none", "failed" ou "passed".
SCENARIOS = [
    {"read": False, "quiz": "none", "challenges": 0},       # 0 %
    {"read": False, "quiz": "failed", "challenges": 0},     # 0 % avec essai raté
    {"read": True, "quiz": "none", "challenges": 0},        # 25 % lecture
    {"read": False, "quiz": "passed", "challenges": 0},      # 25 % quiz
    {"read": False, "quiz": "none", "challenges": 1},        # 25 % défi
    {"read": True, "quiz": "passed", "challenges": 0},       # 50 %
    {"read": True, "quiz": "none", "challenges": 1},         # 50 %
    {"read": False, "quiz": "passed", "challenges": 1},       # 50 %
    {"read": False, "quiz": "failed", "challenges": 2},       # 50 %
    {"read": True, "quiz": "passed", "challenges": 1},        # 75 %
    {"read": True, "quiz": "none", "challenges": 2},          # 75 %
    {"read": False, "quiz": "passed", "challenges": 2},       # 75 %
    {"read": True, "quiz": "passed", "challenges": 2},        # 100 %
]


class Command(BaseCommand):
    help = (
        "Crée des progressions aléatoires de démonstration, avec des utilisateurs "
        "à 0 %, 25 %, 50 %, 75 % ou 100 %."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        modules = list(Module.objects.filter(est_publie=True).order_by("ordre"))
        if not modules:
            raise CommandError("Alefaso aloha: python manage.py seed_formations_mg")

        ConfigurationNiveau.objects.update_or_create(
            pk=1,
            defaults={
                "modules_pour_apprenti": 2,
                "modules_pour_actif": 3,
                "modules_pour_leader": 4,
            },
        )

        users = list(
            User.objects.filter(
                email__in=DEMO_EMAILS,
                role=User.Role.MODERATOR,
                is_active=True,
                is_email_verified=True,
            ).order_by("email")
        )
        if not users:
            raise CommandError("Alefaso aloha: python manage.py seed_users")

        # Suppression des anciennes données de démonstration pour que les
        # badges/certificats restent cohérents avec les nouveaux pourcentages.
        BadgeUtilisateur.objects.filter(utilisateur__in=users).delete()
        Certificat.objects.filter(utilisateur__in=users).delete()
        Notification.objects.filter(destinataire__in=users).delete()
        TentativeQuiz.objects.filter(utilisateur__in=users).delete()
        DefiUtilisateur.objects.filter(utilisateur__in=users).delete()
        ProgressionModule.objects.filter(utilisateur__in=users).delete()

        for user in users:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.level = "beginner"
            profile.save(update_fields=["level"])

        rng = random.SystemRandom()
        assignments = [
            (user, module)
            for user in users
            for module in modules
        ]
        rng.shuffle(assignments)

        # On garantit au minimum une progression 0 %, une 25 % et une 100 %,
        # puis le reste est entièrement distribué au hasard.
        forced = [SCENARIOS[0], SCENARIOS[2], SCENARIOS[-1]]

        for index, (user, module) in enumerate(assignments):
            scenario = forced[index] if index < len(forced) else rng.choice(SCENARIOS)
            self._apply_scenario(user, module, scenario, rng)

        self.stdout.write(
            self.style.SUCCESS(
                "Progressions aléatoires, notifications, badges et certificats seedés."
            )
        )

    def _apply_scenario(self, user, module, scenario, rng):
        now = timezone.now()
        progression = ProgressionModule.objects.create(
            utilisateur=user,
            module=module,
            est_lu=scenario["read"],
            lu_le=now if scenario["read"] else None,
        )

        quiz = getattr(module, "quiz", None)
        quiz_state = scenario["quiz"]
        if quiz is not None and quiz_state != "none":
            passed = quiz_state == "passed"
            score = rng.randint(70, 100) if passed else rng.randint(0, 59)
            total = quiz.points_total_banque
            TentativeQuiz.objects.create(
                utilisateur=user,
                quiz=quiz,
                statut=TentativeQuiz.Statut.SOUMISE,
                score=score,
                points_obtenus=round(total * score / 100),
                points_total=total,
                est_reussi=passed,
                soumise_le=now,
            )

        challenges = list(
            Defi.objects.filter(module=module, est_publie=True).order_by("ordre")
        )
        completed_count = min(scenario["challenges"], 2, len(challenges))
        completed_ids = {challenge.pk for challenge in challenges[:completed_count]}

        for challenge in challenges:
            if challenge.pk in completed_ids:
                status = DefiUtilisateur.Statut.TERMINE
                unlocked_at = started_at = finished_at = now
            else:
                # Les défis restants peuvent être verrouillés, disponibles ou en cours.
                status = rng.choice(
                    [
                        DefiUtilisateur.Statut.VERROUILLE,
                        DefiUtilisateur.Statut.DISPONIBLE,
                        DefiUtilisateur.Statut.EN_COURS,
                    ]
                )
                unlocked_at = now if status != DefiUtilisateur.Statut.VERROUILLE else None
                started_at = now if status == DefiUtilisateur.Statut.EN_COURS else None
                finished_at = None

            DefiUtilisateur.objects.create(
                utilisateur=user,
                defi=challenge,
                statut=status,
                debloque_le=unlocked_at,
                commence_le=started_at,
                termine_le=finished_at,
            )

        # Recalcule le pourcentage et attribue badge/certificat uniquement à 100 %.
        progression = synchroniser_progression_module(user, module)

        if progression.pourcentage < 100:
            notifier(
                user,
                Notification.Type.AUTRE,
                f"Fandrosoana — {module.titre}",
                f"Efa mahatratra {progression.pourcentage}% ny fandrosoanao amin'ity module ity.",
                f"/formation/modules/{module.uuid}/",
            )
