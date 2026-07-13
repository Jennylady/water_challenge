from django.db import transaction
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import IllustrationModule, Module


def _programmer_suppression(fichier):
    """Supprime le fichier du storage uniquement après validation de la transaction."""
    if not fichier or not getattr(fichier, 'name', None):
        return
    storage = fichier.storage
    nom = fichier.name

    def supprimer():
        if storage.exists(nom):
            storage.delete(nom)

    transaction.on_commit(supprimer)


def _ancien_fichier(instance, champ):
    if not instance.pk:
        return None
    ancien = instance.__class__.objects.filter(pk=instance.pk).only(champ).first()
    return getattr(ancien, champ, None) if ancien else None


@receiver(pre_save, sender=Module)
def nettoyer_fichiers_module_remplaces(sender, instance, **kwargs):
    for champ in ('image_couverture', 'video'):
        ancien = _ancien_fichier(instance, champ)
        nouveau = getattr(instance, champ, None)
        ancien_nom = getattr(ancien, 'name', None)
        nouveau_nom = getattr(nouveau, 'name', None)
        nouveau_non_enregistre = nouveau is not None and not getattr(nouveau, '_committed', True)
        if ancien_nom and (ancien_nom != nouveau_nom or nouveau_non_enregistre):
            _programmer_suppression(ancien)


@receiver(post_delete, sender=Module)
def nettoyer_fichiers_module_supprimes(sender, instance, **kwargs):
    _programmer_suppression(instance.image_couverture)
    _programmer_suppression(instance.video)


@receiver(pre_save, sender=IllustrationModule)
def nettoyer_illustration_remplacee(sender, instance, **kwargs):
    ancien = _ancien_fichier(instance, 'image')
    nouveau_non_enregistre = instance.image is not None and not getattr(instance.image, '_committed', True)
    if getattr(ancien, 'name', None) and (
        ancien.name != getattr(instance.image, 'name', None) or nouveau_non_enregistre
    ):
        _programmer_suppression(ancien)


@receiver(post_delete, sender=IllustrationModule)
def nettoyer_illustration_supprimee(sender, instance, **kwargs):
    _programmer_suppression(instance.image)
