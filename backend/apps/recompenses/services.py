from django.db import transaction
from apps.formation.models import ProgressionModule
from apps.notifications.models import Notification
from apps.notifications.services import notifier
from .models import Badge, BadgeUtilisateur, Certificat, ConfigurationNiveau

LEVELS=[('beginner','Débutant'),('apprentice','Apprenti Ambassadeur'),('active','Ambassadeur actif'),('leader','Leader communautaire')]

def synchroniser_progression_module(utilisateur,module):
    with transaction.atomic():
        progression,_=ProgressionModule.objects.select_for_update().get_or_create(utilisateur=utilisateur,module=module)
        avant=progression.est_termine
        progression.recalculer()
        if progression.est_termine and not avant:
            badge,_=Badge.objects.get_or_create(nom=f'Badge — {module.titre}',defaults={'description':f'Module « {module.titre} » terminé avec succès.'})
            _,cree=BadgeUtilisateur.objects.get_or_create(utilisateur=utilisateur,module=module,defaults={'badge':badge})
            if cree:
                notifier(utilisateur,Notification.Type.BADGE_OBTENU,'Nouveau badge obtenu',f'Vous avez obtenu le badge du module « {module.titre} ».')
            synchroniser_niveau(utilisateur)
        return progression

def synchroniser_niveau(utilisateur):
    profile=utilisateur.profile
    cfg=ConfigurationNiveau.charger()
    nb=ProgressionModule.objects.filter(utilisateur=utilisateur,est_termine=True).count()
    nouveau='beginner'
    if nb>=cfg.modules_pour_leader: nouveau='leader'
    elif nb>=cfg.modules_pour_actif: nouveau='active'
    elif nb>=cfg.modules_pour_apprenti: nouveau='apprentice'
    if profile.level!=nouveau:
        profile.level=nouveau; profile.save(update_fields=['level'])
        titre=dict(LEVELS)[nouveau]
        Certificat.objects.get_or_create(utilisateur=utilisateur,niveau=nouveau,defaults={'titre':f'Certificat — {titre}'})
        notifier(utilisateur,Notification.Type.NIVEAU_ATTEINT,'Nouveau niveau atteint',f'Félicitations, vous êtes maintenant {titre}.')
        notifier(utilisateur,Notification.Type.CERTIFICAT_DELIVRE,'Certificat disponible',f'Votre certificat de niveau {titre} est disponible.')
    return nouveau

def reward_challenge_handler(utilisateur,soumission,**kwargs):
    if soumission.defi.module_id:
        synchroniser_progression_module(utilisateur,soumission.defi.module)
