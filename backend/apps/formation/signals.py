from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import ImageIllustrationModule, Module, RessourceModule


def _programmer_suppression(fichier):
    """Supprime le fichier du stockage après validation de la transaction."""
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


def _fichier_a_ete_remplace(ancien, nouveau):
    ancien_nom = getattr(ancien, 'name', None)
    nouveau_nom = getattr(nouveau, 'name', None)
    nouveau_non_enregistre = (
        nouveau is not None and not getattr(nouveau, '_committed', True)
    )
    return bool(
        ancien_nom
        and (ancien_nom != nouveau_nom or nouveau_non_enregistre)
    )


@receiver(pre_save, sender=Module)
def nettoyer_fichiers_module_remplaces(sender, instance, **kwargs):
    for champ in ('image_couverture', 'video'):
        ancien = _ancien_fichier(instance, champ)
        nouveau = getattr(instance, champ, None)
        if _fichier_a_ete_remplace(ancien, nouveau):
            _programmer_suppression(ancien)


@receiver(post_delete, sender=Module)
def nettoyer_fichiers_module_supprimes(sender, instance, **kwargs):
    _programmer_suppression(instance.image_couverture)
    _programmer_suppression(instance.video)


@receiver(pre_save, sender=ImageIllustrationModule)
def nettoyer_image_illustration_remplacee(sender, instance, **kwargs):
    ancien = _ancien_fichier(instance, 'image')
    if _fichier_a_ete_remplace(ancien, instance.image):
        _programmer_suppression(ancien)


@receiver(post_delete, sender=ImageIllustrationModule)
def nettoyer_image_illustration_supprimee(sender, instance, **kwargs):
    _programmer_suppression(instance.image)


@receiver(pre_save, sender=RessourceModule)
def nettoyer_ressource_remplacee(sender, instance, **kwargs):
    ancien = _ancien_fichier(instance, 'fichier')
    if _fichier_a_ete_remplace(ancien, instance.fichier):
        _programmer_suppression(ancien)


@receiver(post_delete, sender=RessourceModule)
def nettoyer_ressource_supprimee(sender, instance, **kwargs):
    _programmer_suppression(instance.fichier)


@receiver(post_save, sender=Module)
def notifier_nouveau_module(sender, instance, created, **kwargs):
    if not created or not instance.est_publie:
        return

    def envoyer():
        from apps.accounts.user.models import User
        from apps.notifications.models import Notification
        from apps.notifications.services import notifier

        utilisateurs = User.objects.filter(
            role='moderator',
            is_active=True,
            is_email_verified=True,
        )
        for utilisateur in utilisateurs:
            notifier(
                utilisateur,
                Notification.Type.NOUVEAU_MODULE,
                'Nouveau module disponible',
                f'Le module « {instance.titre} » est disponible.',
                f'/formation/modules/{instance.slug}/',
            )

    transaction.on_commit(envoyer)
