import logging
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.module_loading import import_string

from apps.accounts.user.models import Profile

from .models import Defi, DefiUtilisateur, PhotoSoumission, SoumissionActivite, Validation
from .signals import defi_debloque, soumission_envoyee, soumission_traitee


logger = logging.getLogger(__name__)


class RegleMetierChallenge(Exception):
    """Erreur métier affichable au client de l'API."""


NIVEAU_RANG_DEFI = {
    Defi.Niveau.DEBUTANT: 0,
    Defi.Niveau.APPRENTI: 1,
    Defi.Niveau.ACTIF: 2,
    Defi.Niveau.LEADER: 3,
}

NIVEAU_RANG_PROFILE = {
    Profile.Level.BEGINNER: 0,
    Profile.Level.APPRENTICE: 1,
    Profile.Level.ACTIVE: 2,
    Profile.Level.LEADER: 3,
}

NIVEAU_RANG_MODULE = {
    'débutant': 0,
    'debutant': 0,
    'apprenti': 1,
    'actif': 2,
    'leader': 3,
}

BADGES_PAR_NIVEAU_PAR_DEFAUT = {
    Profile.Level.BEGINNER: "Goutte d'eau",
    Profile.Level.APPRENTICE: "Protecteur de l'eau",
    Profile.Level.ACTIVE: "Ambassadeur actif",
    Profile.Level.LEADER: "Leader communautaire",
}

IMAGE_MIME_AUTORISES = {'image/jpeg', 'image/png', 'image/webp'}
VIDEO_MIME_AUTORISES = {'video/mp4', 'video/webm', 'video/quicktime'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov'}


def _profile_utilisateur(utilisateur, verrouiller=False):
    queryset = Profile.objects
    if verrouiller:
        queryset = queryset.select_for_update()
    profile = queryset.filter(user_id=utilisateur.id).first()
    if profile is None:
        profile = Profile.objects.create(user_id=utilisateur.id)
        if verrouiller:
            profile = Profile.objects.select_for_update().get(pk=profile.pk)
    return profile


def rang_niveau_utilisateur(utilisateur):
    profile = _profile_utilisateur(utilisateur)
    return NIVEAU_RANG_PROFILE.get(profile.level, 0)


def niveau_defi_autorise(utilisateur, defi):
    return NIVEAU_RANG_DEFI.get(defi.niveau, 0) <= rang_niveau_utilisateur(utilisateur)


def quiz_reussi_pour_defi(utilisateur, defi):
    """Compatibilité : le quiz n'est plus un prérequis pour un défi."""
    return True


def defi_peut_etre_debloque(
    utilisateur,
    defi,
    *,
    rang_utilisateur=None,
):
    """Un défi dépend uniquement de son ouverture et du niveau de l'utilisateur."""
    if rang_utilisateur is None:
        rang_utilisateur = rang_niveau_utilisateur(utilisateur)
    niveau_autorise = NIVEAU_RANG_DEFI.get(defi.niveau, 0) <= rang_utilisateur
    return defi.est_accessible and niveau_autorise

def synchroniser_defis_utilisateur(utilisateur):
    """
    Crée les suivis manquants et synchronise les états verrouillé/disponible.
    Un défi déjà commencé ou terminé n'est jamais rétrogradé automatiquement.
    """
    defis = list(Defi.objects.filter(est_actif=True, est_publie=True).select_related('module'))
    suivis_existants = {
        suivi.defi_id: suivi
        for suivi in DefiUtilisateur.objects.filter(
            utilisateur_id=utilisateur.id,
            defi_id__in=[defi.id for defi in defis],
        )
    }

    a_creer = []
    maintenant = timezone.now()
    debloques = []
    rang_utilisateur = rang_niveau_utilisateur(utilisateur)

    for defi in defis:
        suivi = suivis_existants.get(defi.id)
        peut_debloquer = defi_peut_etre_debloque(
            utilisateur,
            defi,
            rang_utilisateur=rang_utilisateur,
        )

        if suivi is None:
            statut = (
                DefiUtilisateur.Statut.DISPONIBLE
                if peut_debloquer
                else DefiUtilisateur.Statut.VERROUILLE
            )
            suivi = DefiUtilisateur(
                utilisateur_id=utilisateur.id,
                defi=defi,
                statut=statut,
                debloque_le=maintenant if statut == DefiUtilisateur.Statut.DISPONIBLE else None,
            )
            a_creer.append(suivi)
            suivis_existants[defi.id] = suivi
            if statut == DefiUtilisateur.Statut.DISPONIBLE:
                debloques.append(defi)
            continue

        if suivi.statut == DefiUtilisateur.Statut.VERROUILLE and peut_debloquer:
            suivi.statut = DefiUtilisateur.Statut.DISPONIBLE
            suivi.debloque_le = suivi.debloque_le or maintenant
            suivi.save(update_fields=['statut', 'debloque_le', 'modifie_le'])
            debloques.append(defi)
        elif suivi.statut == DefiUtilisateur.Statut.DISPONIBLE and not peut_debloquer:
            suivi.statut = DefiUtilisateur.Statut.VERROUILLE
            suivi.debloque_le = None
            suivi.save(update_fields=['statut', 'debloque_le', 'modifie_le'])

    if a_creer:
        DefiUtilisateur.objects.bulk_create(a_creer, ignore_conflicts=True)
        suivis_existants = {
            suivi.defi_id: suivi
            for suivi in DefiUtilisateur.objects.filter(
                utilisateur_id=utilisateur.id,
                defi_id__in=[defi.id for defi in defis],
            )
        }

    for defi in debloques:
        defi_debloque.send_robust(
            sender=DefiUtilisateur,
            utilisateur=utilisateur,
            defi=defi,
        )
        _executer_hook(
            'CHALLENGES_NOTIFICATION_HANDLER',
            evenement='defi_debloque',
            utilisateur=utilisateur,
            defi=defi,
        )

    return suivis_existants


def debloquer_defis_du_module(utilisateur, module):
    """
    Compatibilité avec les anciens appels : synchronise les défis du module sans
    vérifier la réussite d'un quiz.
    """
    avant = {
        suivi.defi_id: suivi.statut
        for suivi in DefiUtilisateur.objects.filter(
            utilisateur_id=utilisateur.id,
            defi__module=module,
        )
    }
    suivis = synchroniser_defis_utilisateur(utilisateur)
    return [
        suivi.defi
        for defi_id, suivi in suivis.items()
        if suivi.defi.module_id == module.id
        and suivi.statut == DefiUtilisateur.Statut.DISPONIBLE
        and avant.get(defi_id) != DefiUtilisateur.Statut.DISPONIBLE
    ]

def demarrer_defi(utilisateur, defi):
    if not defi.est_accessible:
        raise RegleMetierChallenge("Ce défi est actuellement fermé ou non publié.")

    synchroniser_defis_utilisateur(utilisateur)
    with transaction.atomic():
        suivi = DefiUtilisateur.objects.select_for_update().filter(
            utilisateur_id=utilisateur.id,
            defi=defi,
        ).first()
        if suivi is None or suivi.statut == DefiUtilisateur.Statut.VERROUILLE:
            raise RegleMetierChallenge(
                "Ce défi n'est pas disponible pour votre niveau ou durant cette période."
            )
        if suivi.statut == DefiUtilisateur.Statut.TERMINE:
            raise RegleMetierChallenge("Ce défi est déjà terminé.")
        if suivi.statut == DefiUtilisateur.Statut.DISPONIBLE:
            suivi.statut = DefiUtilisateur.Statut.EN_COURS
            suivi.commence_le = suivi.commence_le or timezone.now()
            suivi.save(update_fields=['statut', 'commence_le', 'modifie_le'])
        return suivi


def _taille_max_octets(nom_setting, valeur_mo_par_defaut):
    return int(getattr(settings, nom_setting, valeur_mo_par_defaut)) * 1024 * 1024


def _valider_fichier(fichier, *, type_fichier):
    if fichier is None:
        return

    if type_fichier == 'image':
        mimes = IMAGE_MIME_AUTORISES
        extensions = IMAGE_EXTENSIONS
        taille_max = _taille_max_octets('CHALLENGE_MAX_IMAGE_SIZE_MB', 8)
    else:
        mimes = VIDEO_MIME_AUTORISES
        extensions = VIDEO_EXTENSIONS
        taille_max = _taille_max_octets('CHALLENGE_MAX_VIDEO_SIZE_MB', 100)

    content_type = (getattr(fichier, 'content_type', '') or '').lower()
    extension = Path(getattr(fichier, 'name', '') or '').suffix.lower()

    if content_type and content_type not in mimes:
        raise RegleMetierChallenge(
            f"Type de {type_fichier} non autorisé : {content_type}."
        )
    if extension not in extensions:
        raise RegleMetierChallenge(
            f"Extension de {type_fichier} non autorisée : {extension or 'inconnue'}."
        )
    if getattr(fichier, 'size', 0) > taille_max:
        raise RegleMetierChallenge(
            f"Le fichier {getattr(fichier, 'name', '')} dépasse la taille maximale autorisée."
        )


def creer_soumission(
    *,
    utilisateur,
    defi,
    rapport,
    date_activite,
    lieu,
    nombre_personnes_sensibilisees,
    photos,
    video=None,
):
    if not defi.est_accessible:
        raise RegleMetierChallenge("Ce défi est actuellement fermé.")
    if not rapport or not str(rapport).strip():
        raise RegleMetierChallenge("Le rapport est requis.")
    if not lieu or not str(lieu).strip():
        raise RegleMetierChallenge("Le lieu est requis.")
    if date_activite > timezone.localdate():
        raise RegleMetierChallenge("La date de l'activité ne peut pas être dans le futur.")
    if nombre_personnes_sensibilisees < 0:
        raise RegleMetierChallenge("Le nombre de personnes sensibilisées ne peut pas être négatif.")

    photos = list(photos or [])
    if len(photos) < defi.nombre_photos_min:
        raise RegleMetierChallenge(
            f"Au moins {defi.nombre_photos_min} photo(s) sont requises."
        )
    if len(photos) > defi.nombre_photos_max:
        raise RegleMetierChallenge(
            f"Au maximum {defi.nombre_photos_max} photo(s) sont autorisées."
        )
    if defi.video_obligatoire and video is None:
        raise RegleMetierChallenge("Une vidéo est obligatoire pour ce défi.")

    for photo in photos:
        _valider_fichier(photo, type_fichier='image')
    if video is not None:
        _valider_fichier(video, type_fichier='video')

    synchroniser_defis_utilisateur(utilisateur)

    with transaction.atomic():
        suivi = DefiUtilisateur.objects.select_for_update().filter(
            utilisateur_id=utilisateur.id,
            defi=defi,
        ).first()
        if suivi is None or suivi.statut == DefiUtilisateur.Statut.VERROUILLE:
            raise RegleMetierChallenge(
                "Ce défi n'est pas disponible pour votre niveau ou durant cette période."
            )
        if suivi.statut == DefiUtilisateur.Statut.TERMINE:
            raise RegleMetierChallenge("Ce défi a déjà été validé.")
        if SoumissionActivite.objects.select_for_update().filter(
            utilisateur_id=utilisateur.id,
            defi=defi,
            statut=SoumissionActivite.Statut.EN_ATTENTE,
        ).exists():
            raise RegleMetierChallenge(
                "Une soumission est déjà en attente de validation pour ce défi."
            )

        if suivi.statut == DefiUtilisateur.Statut.DISPONIBLE:
            suivi.statut = DefiUtilisateur.Statut.EN_COURS
            suivi.commence_le = suivi.commence_le or timezone.now()
            suivi.save(update_fields=['statut', 'commence_le', 'modifie_le'])

        soumission = SoumissionActivite.objects.create(
            utilisateur_id=utilisateur.id,
            defi=defi,
            rapport=str(rapport).strip(),
            date_activite=date_activite,
            lieu=str(lieu).strip(),
            nombre_personnes_sensibilisees=nombre_personnes_sensibilisees,
            video=video,
        )
        for index, photo in enumerate(photos):
            PhotoSoumission.objects.create(
                soumission=soumission, image=photo, ordre=index
            )

    soumission_envoyee.send_robust(
        sender=SoumissionActivite,
        utilisateur=utilisateur,
        soumission=soumission,
    )
    _executer_hook(
        'CHALLENGES_NOTIFICATION_HANDLER',
        evenement='soumission_envoyee',
        utilisateur=utilisateur,
        soumission=soumission,
    )
    return soumission


def annuler_soumission(utilisateur, soumission):
    with transaction.atomic():
        soumission = SoumissionActivite.objects.select_for_update().filter(
            pk=soumission.pk,
            utilisateur_id=utilisateur.id,
        ).first()
        if soumission is None:
            raise RegleMetierChallenge("Soumission introuvable.")
        if soumission.statut != SoumissionActivite.Statut.EN_ATTENTE:
            raise RegleMetierChallenge(
                "Seule une soumission encore en attente peut être annulée."
            )
        defi_id = soumission.defi_id
        soumission.delete()
        suivi = DefiUtilisateur.objects.select_for_update().filter(
            utilisateur_id=utilisateur.id,
            defi_id=defi_id,
        ).first()
        if suivi and suivi.statut != DefiUtilisateur.Statut.TERMINE:
            suivi.statut = DefiUtilisateur.Statut.EN_COURS
            suivi.save(update_fields=['statut', 'modifie_le'])


def _badge_courant(profile):
    badges = getattr(settings, 'CHALLENGE_LEVEL_BADGES', BADGES_PAR_NIVEAU_PAR_DEFAUT)
    return badges.get(profile.level, BADGES_PAR_NIVEAU_PAR_DEFAUT.get(profile.level))


def _mettre_a_jour_progression_profile(utilisateur, profile):
    rang = NIVEAU_RANG_PROFILE.get(profile.level, 0)
    niveaux_autorises = [niveau for niveau, valeur in NIVEAU_RANG_DEFI.items() if valeur <= rang]
    total = Defi.objects.filter(
        est_actif=True,
        est_publie=True,
        est_obligatoire=True,
        niveau__in=niveaux_autorises,
    ).count()
    termines = DefiUtilisateur.objects.filter(
        utilisateur_id=utilisateur.id,
        defi__est_actif=True,
        defi__est_publie=True,
        defi__est_obligatoire=True,
        defi__niveau__in=niveaux_autorises,
        statut=DefiUtilisateur.Statut.TERMINE,
    ).count()
    profile.progression = round((termines / total) * 100) if total else 0


def valider_soumission(*, soumission, validateur, decision, commentaire=None, points=None):
    if decision not in {Validation.Decision.ACCEPTEE, Validation.Decision.REFUSEE}:
        raise RegleMetierChallenge("Décision invalide.")
    if soumission.utilisateur_id == validateur.id:
        raise RegleMetierChallenge("Un validateur ne peut pas traiter sa propre soumission.")
    if decision == Validation.Decision.REFUSEE and not (commentaire or '').strip():
        raise RegleMetierChallenge("Un commentaire est obligatoire en cas de refus.")

    with transaction.atomic():
        soumission = SoumissionActivite.objects.select_for_update().select_related(
            'utilisateur', 'defi'
        ).filter(pk=soumission.pk).first()
        if soumission is None:
            raise RegleMetierChallenge("Soumission introuvable.")
        if soumission.statut != SoumissionActivite.Statut.EN_ATTENTE:
            raise RegleMetierChallenge("Cette soumission a déjà été traitée.")
        if Validation.objects.filter(soumission=soumission).exists():
            raise RegleMetierChallenge("Cette soumission possède déjà une validation.")

        points_attribues = 0
        if decision == Validation.Decision.ACCEPTEE:
            points_attribues = soumission.defi.points_recompense if points is None else int(points)
            if points_attribues < 0:
                raise RegleMetierChallenge("Les points attribués ne peuvent pas être négatifs.")

        validation = Validation.objects.create(
            soumission=soumission,
            validateur=validateur,
            decision=decision,
            commentaire=(commentaire or '').strip() or None,
            points_attribues=points_attribues,
            points_appliques=False,
        )

        maintenant = timezone.now()
        suivi, _ = DefiUtilisateur.objects.select_for_update().get_or_create(
            utilisateur_id=soumission.utilisateur_id,
            defi=soumission.defi,
        )

        if decision == Validation.Decision.ACCEPTEE:
            soumission.statut = SoumissionActivite.Statut.VALIDEE
            suivi.statut = DefiUtilisateur.Statut.TERMINE
            suivi.termine_le = maintenant
            suivi.commence_le = suivi.commence_le or soumission.soumis_le

            profile = _profile_utilisateur(soumission.utilisateur, verrouiller=True)
            Profile.objects.filter(pk=profile.pk).update(points=F('points') + points_attribues)
            profile.refresh_from_db(fields=['points', 'level', 'progression', 'current_badge'])
            profile.update_level()
            profile.refresh_from_db(fields=['points', 'level', 'progression', 'current_badge'])
            profile.current_badge = _badge_courant(profile)
            _mettre_a_jour_progression_profile(soumission.utilisateur, profile)
            profile.save(update_fields=['current_badge', 'progression', 'updated_at'])

            validation.points_appliques = True
            validation.save(update_fields=['points_appliques'])
        else:
            soumission.statut = SoumissionActivite.Statut.REFUSEE
            suivi.statut = DefiUtilisateur.Statut.EN_COURS
            suivi.termine_le = None

        soumission.traitee_le = maintenant
        soumission.save(update_fields=['statut', 'traitee_le', 'modifie_le'])
        suivi.save(update_fields=['statut', 'commence_le', 'termine_le', 'modifie_le'])

    soumission_traitee.send_robust(
        sender=Validation,
        soumission=soumission,
        validation=validation,
        utilisateur=soumission.utilisateur,
    )
    _executer_hook(
        'CHALLENGES_NOTIFICATION_HANDLER',
        evenement='soumission_traitee',
        utilisateur=soumission.utilisateur,
        soumission=soumission,
        validation=validation,
    )
    if decision == Validation.Decision.ACCEPTEE:
        _executer_hook(
            'CHALLENGES_REWARD_HANDLER',
            utilisateur=soumission.utilisateur,
            soumission=soumission,
            validation=validation,
        )
    return validation


def est_module_debloque_pour_utilisateur(utilisateur, module):
    """
    Les modules ne dépendent plus du module précédent, d'un quiz ou d'un défi.
    Seuls leur état d'ouverture et le niveau de l'utilisateur sont pris en compte.
    """
    profile = _profile_utilisateur(utilisateur)
    rang_profile = NIVEAU_RANG_PROFILE.get(profile.level, 0)
    rang_module = NIVEAU_RANG_MODULE.get(module.niveau, 0)
    return module.est_accessible and rang_module <= rang_profile

def _executer_hook(nom_setting, **kwargs):
    chemin = getattr(settings, nom_setting, None)
    if not chemin:
        return None
    try:
        fonction = import_string(chemin)
        return fonction(**kwargs)
    except Exception:
        logger.exception("Échec du hook %s (%s).", nom_setting, chemin)
        return None