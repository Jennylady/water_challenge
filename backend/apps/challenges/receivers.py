import logging

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.formation.models import TentativeQuiz

from .models import Defi, PhotoSoumission, SoumissionActivite


logger = logging.getLogger(__name__)


@receiver(post_save, sender=TentativeQuiz)
def debloquer_defis_apres_quiz_reussi(sender, instance, created, **kwargs):
    """Le défi se débloque automatiquement dès qu'une tentative de quiz est réussie."""
    if not created or not instance.est_reussi:
        return

    utilisateur_id = instance.utilisateur_id
    module_id = instance.quiz.module_id

    def _executer():
        from apps.accounts.user.models import User
        from apps.formation.models import Module
        from .services import debloquer_defis_du_module

        utilisateur = User.objects.filter(
            pk=utilisateur_id
        ).first()

        module = Module.objects.filter(
            pk=module_id
        ).first()

        if utilisateur is not None and module is not None:
            try:
                debloquer_defis_du_module(utilisateur, module)
            except Exception:
                logger.exception(
                    "Impossible de débloquer les défis du module %s "
                    "pour l'utilisateur %s.",
                    module_id,
                    utilisateur_id,
                )

    transaction.on_commit(_executer)


def _supprimer_fichier(field_file):
    if not field_file:
        return
    nom = getattr(field_file, 'name', None)
    stockage = getattr(field_file, 'storage', None)
    if nom and stockage:
        transaction.on_commit(lambda: stockage.delete(nom))


@receiver(post_delete, sender=PhotoSoumission)
def supprimer_photo_physique(sender, instance, **kwargs):
    _supprimer_fichier(instance.image)


@receiver(post_delete, sender=SoumissionActivite)
def supprimer_video_physique(sender, instance, **kwargs):
    _supprimer_fichier(instance.video)


@receiver(post_delete, sender=Defi)
def supprimer_couverture_physique(sender, instance, **kwargs):
    _supprimer_fichier(instance.image_couverture)