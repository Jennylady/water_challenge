from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.user.models import Profile, User
from apps.challenges.models import Defi, DefiUtilisateur
from apps.formation.models import Module, ProgressionModule, TentativeQuiz
from apps.notifications.models import Notification
from apps.notifications.services import notifier
from apps.recompenses.models import ConfigurationNiveau
from apps.recompenses.services import synchroniser_progression_module


# Nombre de modules entièrement terminés par utilisateur.
COMPLETED_MODULES = {
    "jennysc@gmail.com": 3,
    "moderateur@water.mg": 2,
    "fano@water.mg": 1,
    "saholy@water.mg": 0,
}


class Command(BaseCommand):
    help = "Crée des progressions de démonstration et déclenche notifications, badges et certificats."

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

        for email, completed_count in COMPLETED_MODULES.items():
            user = User.objects.filter(email=email).first()
            if user is None:
                self.stdout.write(self.style.WARNING(f"Utilisateur tsy hita: {email}"))
                continue

            Profile.objects.get_or_create(user=user)

            for module in modules:
                progression, _ = ProgressionModule.objects.get_or_create(
                    utilisateur=user,
                    module=module,
                )

            for module in modules[:completed_count]:
                progression = ProgressionModule.objects.get(utilisateur=user, module=module)
                progression.est_lu = True
                progression.lu_le = progression.lu_le or timezone.now()
                progression.save(update_fields=["est_lu", "lu_le"])

                quiz = getattr(module, "quiz", None)
                if quiz is not None:
                    attempt, _ = TentativeQuiz.objects.update_or_create(
                        utilisateur=user,
                        quiz=quiz,
                        statut=TentativeQuiz.Statut.SOUMISE,
                        defaults={
                            "score": 100,
                            "points_obtenus": quiz.points_total_banque,
                            "points_total": quiz.points_total_banque,
                            "est_reussi": True,
                            "soumise_le": timezone.now(),
                        },
                    )
                    if not Notification.objects.filter(
                        destinataire=user,
                        type=Notification.Type.QUIZ_DEBLOQUE,
                        titre=f"Quiz réussi — {module.titre}",
                    ).exists():
                        notifier(
                            user,
                            Notification.Type.QUIZ_DEBLOQUE,
                            f"Quiz réussi — {module.titre}",
                            "Nahazo 100% tamin'ny quiz ianao.",
                            f"/formation/modules/{module.uuid}/",
                        )

                challenges = list(Defi.objects.filter(module=module, est_publie=True).order_by("ordre")[:2])
                if len(challenges) < 2:
                    raise CommandError(
                        f"Le module « {module.titre} » doit posséder au moins deux défis."
                    )

                for challenge in challenges:
                    DefiUtilisateur.objects.update_or_create(
                        utilisateur=user,
                        defi=challenge,
                        defaults={
                            "statut": DefiUtilisateur.Statut.TERMINE,
                            "debloque_le": timezone.now(),
                            "commence_le": timezone.now(),
                            "termine_le": timezone.now(),
                        },
                    )
                    if not Notification.objects.filter(
                        destinataire=user,
                        type=Notification.Type.SOUMISSION_VALIDEE,
                        titre=f"Défi validé — {challenge.titre}",
                    ).exists():
                        notifier(
                            user,
                            Notification.Type.SOUMISSION_VALIDEE,
                            f"Défi validé — {challenge.titre}",
                            "Voamarina ny fanatanterahanao ity défi ity.",
                            f"/challenges/defis/{challenge.id}/",
                        )

                # Cette fonction recalcule 100 %, crée le badge du module,
                # met à jour le niveau et délivre le certificat correspondant.
                synchroniser_progression_module(user, module)

            if completed_count == 0 and not Notification.objects.filter(
                destinataire=user,
                type=Notification.Type.AUTRE,
                titre="Manomboka ny fiofanana",
            ).exists():
                notifier(
                    user,
                    Notification.Type.AUTRE,
                    "Manomboka ny fiofanana",
                    "Misafidiana module iray, vakio ny lesona, valio ny quiz ary tanteraho ny défis roa.",
                    "/formation/modules/",
                )

        self.stdout.write(self.style.SUCCESS("Progressions, notifications, badges et certificats seedés."))
