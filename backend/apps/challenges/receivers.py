from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Defi, PhotoSoumission, SoumissionActivite


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