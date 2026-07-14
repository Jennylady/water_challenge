from .models import Notification

def notifier(utilisateur, type_notification, titre, message, lien=None):
    if utilisateur is None:
        return None
    return Notification.objects.create(destinataire=utilisateur, type=type_notification, titre=titre, message=message, lien=lien)

def notification_challenge_handler(evenement, utilisateur, **kwargs):
    if evenement == 'defi_debloque':
        defi = kwargs.get('defi')
        return notifier(utilisateur, Notification.Type.DEFI_DEBLOQUE, 'Défi débloqué', f'Le défi « {defi.titre} » est maintenant disponible.', f'/challenges/defis/{defi.id}/')
    if evenement == 'soumission_envoyee':
        soumission = kwargs.get('soumission')
        return notifier(utilisateur, Notification.Type.AUTRE, 'Soumission reçue', f'Votre activité pour « {soumission.defi.titre} » est en attente de validation.')
    if evenement == 'soumission_traitee':
        validation = kwargs.get('validation'); soumission = kwargs.get('soumission')
        ok = validation.decision == 'acceptee'
        return notifier(utilisateur, Notification.Type.SOUMISSION_VALIDEE if ok else Notification.Type.SOUMISSION_REFUSEE, 'Soumission validée' if ok else 'Soumission refusée', f'Votre soumission pour « {soumission.defi.titre} » a été {"acceptée" if ok else "refusée"}.')
