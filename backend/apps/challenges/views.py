from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Count, ExpressionWrapper, F, IntegerField, Q, Sum
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.user.models import Profile
from apps.accounts.user.permissions import IsModeratorUser
from apps.formation.models import Module

from .models import Defi, DefiUtilisateur, SoumissionActivite, Validation
from apps.accounts.user.permissions import IsValidatorUser
from .serializers import (
    DefiAdminSerializer,
    DefiDetailSerializer,
    DefiListeSerializer,
    DefiPopulaireSerializer,
    ParticipantDefiSerializer,
    SoumissionActiviteSerializer,
)
from .services import (
    RegleMetierChallenge,
    annuler_soumission,
    creer_soumission,
    demarrer_defi,
    synchroniser_defis_utilisateur,
    valider_soumission,
)
from .swaggers import (
    swagger_admin_detail_soumission,
    swagger_admin_liste_defis,
    swagger_admin_liste_soumissions,
    swagger_admin_statistiques,
    swagger_annuler_soumission,
    swagger_commencer_defi,
    swagger_creer_defi,
    swagger_detail_defi,
    swagger_detail_soumission,
    swagger_fermer_defi,
    swagger_liste_defis,
    swagger_mes_soumissions,
    swagger_mes_statistiques,
    swagger_modifier_defi,
    swagger_ouvrir_defi,
    swagger_participants_defi,
    swagger_soumettre_activite,
    swagger_supprimer_defi,
    swagger_valider_soumission,
)


def reponse_succes(nom_attribut, valeur, message=None, http_status=status.HTTP_200_OK):
    payload = {'success': True}
    if message:
        payload['message'] = message
    payload[nom_attribut] = valeur
    return Response(payload, status=http_status)


def reponse_erreur(message, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({'success': False, 'erreur': message}, status=http_status)


def _bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {'true', '1', 'yes', 'oui', 'on'}


def _int(value, default=0, minimum=None):
    try:
        resultat = int(value)
    except (TypeError, ValueError):
        raise RegleMetierChallenge(f"Valeur entière invalide : {value}.")
    if minimum is not None and resultat < minimum:
        raise RegleMetierChallenge(f"La valeur doit être supérieure ou égale à {minimum}.")
    return resultat


def _date_time_ou_none(value, champ):
    if value in (None, ''):
        return None
    resultat = parse_datetime(str(value))
    if resultat is None:
        raise RegleMetierChallenge(
            f"Le champ '{champ}' doit être une date/heure ISO 8601 valide."
        )
    return resultat


def _defi_admin_ou_404(defi_id):
    return Defi.objects.filter(pk=defi_id).select_related('module').first()


def _defi_ambassadeur_ou_404(defi_id):
    return Defi.objects.filter(
        pk=defi_id,
        est_actif=True,
        est_publie=True,
    ).select_related('module').first()


def _contexte_defis(request, utilisateur, suivis, defis):
    soumissions_en_attente = set(
        SoumissionActivite.objects.filter(
            utilisateur_id=utilisateur.id,
            defi_id__in=[defi.id for defi in defis],
            statut=SoumissionActivite.Statut.EN_ATTENTE,
        ).values_list('defi_id', flat=True)
    )
    return {
        'request': request,
        'utilisateur': utilisateur,
        'suivis': suivis,
        'soumissions_en_attente': soumissions_en_attente,
    }


# =============================================================================
# PUBLIC - PAGE D’ACCUEIL
# =============================================================================

class DefisPopulairesPublicView(APIView):
    """Retourne les défis publiés les plus suivis pour la landing page."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            try:
                limite = int(request.query_params.get('limite', 8))
            except (TypeError, ValueError):
                limite = 8

            limite = max(1, min(limite, 12))
            maintenant = timezone.now()

            defis = (
                Defi.objects.filter(
                    est_actif=True,
                    est_publie=True,
                    est_ouvert=True,
                )
                .filter(
                    Q(date_debut__isnull=True) | Q(date_debut__lte=maintenant),
                    Q(date_fin__isnull=True) | Q(date_fin__gte=maintenant),
                )
                .select_related('module')
                .annotate(
                    nombre_participants=Count(
                        'defis_utilisateur__utilisateur_id', distinct=True
                    ),
                    nombre_soumissions=Count('soumissions', distinct=True),
                    nombre_validations=Count(
                        'soumissions',
                        filter=Q(soumissions__statut=SoumissionActivite.Statut.VALIDEE),
                        distinct=True,
                    ),
                )
                .annotate(
                    score_popularite=ExpressionWrapper(
                        F('nombre_participants')
                        + (F('nombre_soumissions') * 2)
                        + (F('nombre_validations') * 3),
                        output_field=IntegerField(),
                    )
                )
                .order_by(
                    '-score_popularite',
                    '-nombre_validations',
                    '-nombre_soumissions',
                    '-nombre_participants',
                    'ordre',
                    '-cree_le',
                )[:limite]
            )

            serializer = DefiPopulaireSerializer(
                defis, many=True, context={'request': request}
            )
            return reponse_succes('defis', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# AMBASSADEUR
# =============================================================================

class ListeDefisAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_liste_defis
    def get(self, request):
        try:
            utilisateur = request.user
            suivis = synchroniser_defis_utilisateur(utilisateur)
            defis = Defi.objects.filter(est_actif=True, est_publie=True).select_related('module')

            niveau = request.query_params.get('niveau')
            if niveau:
                defis = defis.filter(niveau=niveau)
            module_slug = request.query_params.get('module_slug')
            if module_slug:
                defis = defis.filter(module__slug=module_slug)
            est_obligatoire = request.query_params.get('est_obligatoire')
            if est_obligatoire is not None:
                defis = defis.filter(est_obligatoire=_bool(est_obligatoire))

            statut_filtre = request.query_params.get('statut')
            if statut_filtre:
                ids = [
                    defi_id for defi_id, suivi in suivis.items()
                    if suivi.statut == statut_filtre
                ]
                defis = defis.filter(id__in=ids)

            defis = list(defis)
            serializer = DefiListeSerializer(
                defis,
                many=True,
                context=_contexte_defis(request, utilisateur, suivis, defis),
            )
            return reponse_succes('defis', serializer.data)
        except RegleMetierChallenge as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetailDefiAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_detail_defi
    def get(self, request, defi_id):
        try:
            defi = _defi_ambassadeur_ou_404(defi_id)
            if defi is None:
                return reponse_erreur('Défi introuvable.', status.HTTP_404_NOT_FOUND)
            suivis = synchroniser_defis_utilisateur(request.user)
            serializer = DefiDetailSerializer(
                defi,
                context=_contexte_defis(request, request.user, suivis, [defi]),
            )
            return reponse_succes('defi', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommencerDefiAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_commencer_defi
    def post(self, request, defi_id):
        try:
            defi = _defi_ambassadeur_ou_404(defi_id)
            if defi is None:
                return reponse_erreur('Défi introuvable.', status.HTTP_404_NOT_FOUND)
            suivi = demarrer_defi(request.user, defi)
            suivis = {defi.id: suivi}
            serializer = DefiDetailSerializer(
                defi,
                context=_contexte_defis(request, request.user, suivis, [defi]),
            )
            return reponse_succes('defi', serializer.data, message='Défi commencé.')
        except RegleMetierChallenge as exc:
            return reponse_erreur(str(exc), status.HTTP_403_FORBIDDEN)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class SoumettreActiviteAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @swagger_soumettre_activite
    def post(self, request, defi_id):
        try:
            defi = _defi_ambassadeur_ou_404(defi_id)
            if defi is None:
                return reponse_erreur('Défi introuvable.', status.HTTP_404_NOT_FOUND)

            date_activite = parse_date(str(request.data.get('date_activite') or ''))
            if date_activite is None:
                return reponse_erreur(
                    "Le champ 'date_activite' doit être au format AAAA-MM-JJ."
                )

            soumission = creer_soumission(
                utilisateur=request.user,
                defi=defi,
                rapport=request.data.get('rapport'),
                date_activite=date_activite,
                lieu=request.data.get('lieu'),
                nombre_personnes_sensibilisees=_int(
                    request.data.get('nombre_personnes_sensibilisees', 0),
                    minimum=0,
                ),
                photos=request.FILES.getlist('photos'),
                video=request.FILES.get('video'),
            )
            soumission = SoumissionActivite.objects.select_related(
                'utilisateur', 'defi'
            ).prefetch_related('photos').get(pk=soumission.pk)
            serializer = SoumissionActiviteSerializer(
                soumission,
                context={'request': request},
            )
            return reponse_succes(
                'soumission',
                serializer.data,
                message='Activité envoyée pour validation.',
                http_status=status.HTTP_201_CREATED,
            )
        except RegleMetierChallenge as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class MesSoumissionsAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_mes_soumissions
    def get(self, request):
        try:
            soumissions = SoumissionActivite.objects.filter(
                utilisateur_id=request.user.id
            ).select_related('utilisateur', 'defi', 'validation').prefetch_related('photos')

            statut_filtre = request.query_params.get('statut')
            if statut_filtre:
                soumissions = soumissions.filter(statut=statut_filtre)
            defi_id = request.query_params.get('defi_id')
            if defi_id:
                soumissions = soumissions.filter(defi_id=defi_id)

            serializer = SoumissionActiviteSerializer(
                soumissions,
                many=True,
                context={'request': request},
            )
            return reponse_succes('soumissions', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetailSoumissionAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_detail_soumission
    def get(self, request, soumission_id):
        try:
            soumission = SoumissionActivite.objects.filter(
                pk=soumission_id,
                utilisateur_id=request.user.id,
            ).select_related('utilisateur', 'defi', 'validation').prefetch_related('photos').first()
            if soumission is None:
                return reponse_erreur('Soumission introuvable.', status.HTTP_404_NOT_FOUND)
            serializer = SoumissionActiviteSerializer(
                soumission,
                context={'request': request},
            )
            return reponse_succes('soumission', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnnulerSoumissionAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_annuler_soumission
    def delete(self, request, soumission_id):
        try:
            soumission = SoumissionActivite.objects.filter(
                pk=soumission_id,
                utilisateur_id=request.user.id,
            ).first()
            if soumission is None:
                return reponse_erreur('Soumission introuvable.', status.HTTP_404_NOT_FOUND)
            annuler_soumission(request.user, soumission)
            return reponse_succes('soumission', None, message='Soumission annulée.')
        except RegleMetierChallenge as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class MesStatistiquesDefisView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_mes_statistiques
    def get(self, request):
        try:
            synchroniser_defis_utilisateur(request.user)
            suivis = DefiUtilisateur.objects.filter(utilisateur_id=request.user.id)
            soumissions = SoumissionActivite.objects.filter(utilisateur_id=request.user.id)
            profile = Profile.objects.filter(user_id=request.user.id).first()

            statistiques = {
                'defis_verrouilles': suivis.filter(statut=DefiUtilisateur.Statut.VERROUILLE).count(),
                'defis_disponibles': suivis.filter(statut=DefiUtilisateur.Statut.DISPONIBLE).count(),
                'defis_en_cours': suivis.filter(statut=DefiUtilisateur.Statut.EN_COURS).count(),
                'defis_termines': suivis.filter(statut=DefiUtilisateur.Statut.TERMINE).count(),
                'soumissions_en_attente': soumissions.filter(statut=SoumissionActivite.Statut.EN_ATTENTE).count(),
                'soumissions_validees': soumissions.filter(statut=SoumissionActivite.Statut.VALIDEE).count(),
                'soumissions_refusees': soumissions.filter(statut=SoumissionActivite.Statut.REFUSEE).count(),
                'personnes_sensibilisees': soumissions.filter(
                    statut=SoumissionActivite.Statut.VALIDEE
                ).aggregate(total=Sum('nombre_personnes_sensibilisees'))['total'] or 0,
                'points': profile.points if profile else 0,
                'niveau': profile.level if profile else None,
                'progression': profile.progression if profile else 0,
                'badge_courant': profile.current_badge if profile else None,
            }
            return reponse_succes('statistiques', statistiques)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# ADMIN / MODÉRATEUR - DÉFIS
# =============================================================================

class ListeDefisAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_admin_liste_defis
    def get(self, request):
        try:
            defis = Defi.objects.select_related('module').annotate(
                nb_participants_annote=Count('defis_utilisateur', distinct=True),
                nb_termines_annote=Count(
                    'defis_utilisateur',
                    filter=Q(defis_utilisateur__statut=DefiUtilisateur.Statut.TERMINE),
                    distinct=True,
                ),
                nb_en_attente_annote=Count(
                    'soumissions',
                    filter=Q(soumissions__statut=SoumissionActivite.Statut.EN_ATTENTE),
                    distinct=True,
                ),
            )
            niveau = request.query_params.get('niveau')
            if niveau:
                defis = defis.filter(niveau=niveau)
            est_publie = request.query_params.get('est_publie')
            if est_publie is not None:
                defis = defis.filter(est_publie=_bool(est_publie))
            est_actif = request.query_params.get('est_actif')
            if est_actif is not None:
                defis = defis.filter(est_actif=_bool(est_actif))
            module_slug = request.query_params.get('module_slug')
            if module_slug:
                defis = defis.filter(module__slug=module_slug)

            serializer = DefiAdminSerializer(defis, many=True, context={'request': request})
            return reponse_succes('defis', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreerDefiAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @swagger_creer_defi
    def post(self, request):
        try:
            champs_requis = [
                'titre', 'description', 'resultat_attendu',
                'criteres_validation', 'niveau', 'duree_estimee',
            ]
            manquants = [champ for champ in champs_requis if not request.data.get(champ)]
            if manquants:
                return reponse_erreur(
                    f"Champs requis manquants : {', '.join(manquants)}."
                )

            module = None
            module_slug = request.data.get('module_slug')
            if module_slug:
                module = Module.objects.filter(slug=module_slug).first()
                if module is None:
                    return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            defi = Defi(
                module=module,
                titre=str(request.data.get('titre')).strip(),
                description=str(request.data.get('description')).strip(),
                resultat_attendu=str(request.data.get('resultat_attendu')).strip(),
                criteres_validation=str(request.data.get('criteres_validation')).strip(),
                image_couverture=request.FILES.get('image_couverture'),
                niveau=request.data.get('niveau'),
                ordre=_int(request.data.get('ordre', 0), minimum=0),
                duree_estimee=str(request.data.get('duree_estimee')).strip(),
                points_recompense=_int(request.data.get('points_recompense', 10), minimum=0),
                nombre_photos_min=_int(request.data.get('nombre_photos_min', 1), minimum=0),
                nombre_photos_max=_int(request.data.get('nombre_photos_max', 5), minimum=0),
                video_obligatoire=_bool(request.data.get('video_obligatoire')),
                est_obligatoire=_bool(request.data.get('est_obligatoire'), True),
                est_actif=_bool(request.data.get('est_actif'), True),
                est_publie=_bool(request.data.get('est_publie'), True),
                est_ouvert=_bool(request.data.get('est_ouvert'), True),
                date_debut=_date_time_ou_none(request.data.get('date_debut'), 'date_debut'),
                date_fin=_date_time_ou_none(request.data.get('date_fin'), 'date_fin'),
            )
            defi.full_clean()
            defi.save()
            serializer = DefiAdminSerializer(defi, context={'request': request})
            return reponse_succes(
                'defi', serializer.data,
                message='Défi créé.',
                http_status=status.HTTP_201_CREATED,
            )
        except (RegleMetierChallenge, DjangoValidationError) as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModifierDefiAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @swagger_modifier_defi
    def put(self, request, defi_id):
        try:
            defi = _defi_admin_ou_404(defi_id)
            if defi is None:
                return reponse_erreur('Défi introuvable.', status.HTTP_404_NOT_FOUND)

            if 'module_slug' in request.data:
                module_slug = request.data.get('module_slug')
                if module_slug in (None, ''):
                    defi.module = None
                else:
                    module = Module.objects.filter(slug=module_slug).first()
                    if module is None:
                        return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
                    defi.module = module

            for champ in [
                'titre', 'description', 'resultat_attendu', 'criteres_validation',
                'niveau', 'duree_estimee',
            ]:
                if champ in request.data:
                    valeur = request.data.get(champ)
                    if not valeur:
                        return reponse_erreur(f"Le champ '{champ}' ne peut pas être vide.")
                    setattr(defi, champ, str(valeur).strip())

            for champ, minimum in [
                ('ordre', 0), ('points_recompense', 0),
                ('nombre_photos_min', 0), ('nombre_photos_max', 0),
            ]:
                if champ in request.data:
                    setattr(defi, champ, _int(request.data.get(champ), minimum=minimum))

            for champ in [
                'video_obligatoire', 'est_obligatoire', 'est_actif',
                'est_publie', 'est_ouvert',
            ]:
                if champ in request.data:
                    setattr(defi, champ, _bool(request.data.get(champ)))

            if 'date_debut' in request.data:
                defi.date_debut = _date_time_ou_none(request.data.get('date_debut'), 'date_debut')
            if 'date_fin' in request.data:
                defi.date_fin = _date_time_ou_none(request.data.get('date_fin'), 'date_fin')

            ancien_fichier = None
            if 'image_couverture' in request.FILES:
                ancien_fichier = defi.image_couverture
                defi.image_couverture = request.FILES.get('image_couverture')

            defi.full_clean()
            defi.save()
            if ancien_fichier and ancien_fichier.name:
                transaction.on_commit(
                    lambda: ancien_fichier.storage.delete(ancien_fichier.name)
                )

            serializer = DefiAdminSerializer(defi, context={'request': request})
            return reponse_succes('defi', serializer.data, message='Défi modifié.')
        except (RegleMetierChallenge, DjangoValidationError) as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class SupprimerDefiAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_supprimer_defi
    def delete(self, request, defi_id):
        try:
            defi = _defi_admin_ou_404(defi_id)
            if defi is None:
                return reponse_erreur('Défi introuvable.', status.HTTP_404_NOT_FOUND)
            defi.delete()
            return reponse_succes('defi', None, message='Défi supprimé.')
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class OuvrirDefiAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_ouvrir_defi
    def post(self, request, defi_id):
        try:
            defi = _defi_admin_ou_404(defi_id)
            if defi is None:
                return reponse_erreur('Défi introuvable.', status.HTTP_404_NOT_FOUND)
            defi.est_ouvert = True
            defi.save(update_fields=['est_ouvert', 'modifie_le'])
            serializer = DefiAdminSerializer(defi, context={'request': request})
            return reponse_succes('defi', serializer.data, message='Défi ouvert.')
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class FermerDefiAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_fermer_defi
    def post(self, request, defi_id):
        try:
            defi = _defi_admin_ou_404(defi_id)
            if defi is None:
                return reponse_erreur('Défi introuvable.', status.HTTP_404_NOT_FOUND)
            defi.est_ouvert = False
            defi.save(update_fields=['est_ouvert', 'modifie_le'])
            serializer = DefiAdminSerializer(defi, context={'request': request})
            return reponse_succes('defi', serializer.data, message='Défi fermé.')
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParticipantsDefiAdminView(APIView):
    permission_classes = [IsAuthenticated, IsValidatorUser]

    @swagger_participants_defi
    def get(self, request, defi_id):
        try:
            defi = _defi_admin_ou_404(defi_id)
            if defi is None:
                return reponse_erreur('Défi introuvable.', status.HTTP_404_NOT_FOUND)
            participants = DefiUtilisateur.objects.filter(defi=defi).select_related(
                'utilisateur', 'defi'
            )
            statut_filtre = request.query_params.get('statut')
            if statut_filtre:
                participants = participants.filter(statut=statut_filtre)
            serializer = ParticipantDefiSerializer(participants, many=True)
            return reponse_succes('participants', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# ADMIN / VALIDATEUR - SOUMISSIONS
# =============================================================================

class ListeSoumissionsAdminView(APIView):
    permission_classes = [IsAuthenticated, IsValidatorUser]

    @swagger_admin_liste_soumissions
    def get(self, request):
        try:
            soumissions = SoumissionActivite.objects.select_related(
                'utilisateur', 'defi', 'validation'
            ).prefetch_related('photos')
            statut_filtre = request.query_params.get('statut')
            if statut_filtre:
                soumissions = soumissions.filter(statut=statut_filtre)
            defi_id = request.query_params.get('defi_id')
            if defi_id:
                soumissions = soumissions.filter(defi_id=defi_id)
            utilisateur_id = request.query_params.get('utilisateur_id')
            if utilisateur_id:
                soumissions = soumissions.filter(utilisateur_id=utilisateur_id)
            recherche = request.query_params.get('recherche')
            if recherche:
                soumissions = soumissions.filter(
                    Q(utilisateur__email__icontains=recherche)
                    | Q(defi__titre__icontains=recherche)
                    | Q(lieu__icontains=recherche)
                    | Q(rapport__icontains=recherche)
                )
            serializer = SoumissionActiviteSerializer(
                soumissions, many=True, context={'request': request}
            )
            return reponse_succes('soumissions', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetailSoumissionAdminView(APIView):
    permission_classes = [IsAuthenticated, IsValidatorUser]

    @swagger_admin_detail_soumission
    def get(self, request, soumission_id):
        try:
            soumission = SoumissionActivite.objects.filter(pk=soumission_id).select_related(
                'utilisateur', 'defi', 'validation'
            ).prefetch_related('photos').first()
            if soumission is None:
                return reponse_erreur('Soumission introuvable.', status.HTTP_404_NOT_FOUND)
            serializer = SoumissionActiviteSerializer(
                soumission, context={'request': request}
            )
            return reponse_succes('soumission', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValiderSoumissionAdminView(APIView):
    permission_classes = [IsAuthenticated, IsValidatorUser]
    parser_classes = [JSONParser]

    @swagger_valider_soumission
    def post(self, request, soumission_id):
        try:
            soumission = SoumissionActivite.objects.filter(pk=soumission_id).select_related(
                'utilisateur', 'defi'
            ).first()
            if soumission is None:
                return reponse_erreur('Soumission introuvable.', status.HTTP_404_NOT_FOUND)

            points = request.data.get('points_attribues')
            if points is not None:
                points = _int(points, minimum=0)
            validation = valider_soumission(
                soumission=soumission,
                validateur=request.user,
                decision=request.data.get('decision'),
                commentaire=request.data.get('commentaire'),
                points=points,
            )
            soumission = SoumissionActivite.objects.select_related(
                'utilisateur', 'defi', 'validation'
            ).prefetch_related('photos').get(pk=validation.soumission_id)
            serializer = SoumissionActiviteSerializer(
                soumission, context={'request': request}
            )
            message = (
                'Soumission validée et points attribués.'
                if validation.decision == Validation.Decision.ACCEPTEE
                else 'Soumission refusée.'
            )
            return reponse_succes('soumission', serializer.data, message=message)
        except RegleMetierChallenge as exc:
            return reponse_erreur(str(exc), status.HTTP_409_CONFLICT)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class StatistiquesChallengesAdminView(APIView):
    permission_classes = [IsAuthenticated, IsValidatorUser]

    @swagger_admin_statistiques
    def get(self, request):
        try:
            soumissions = SoumissionActivite.objects.all()
            validees = soumissions.filter(statut=SoumissionActivite.Statut.VALIDEE)
            statistiques = {
                'defis_total': Defi.objects.count(),
                'defis_actifs': Defi.objects.filter(est_actif=True, est_publie=True).count(),
                'participants_uniques': DefiUtilisateur.objects.values(
                    'utilisateur_id'
                ).distinct().count(),
                'defis_termines': DefiUtilisateur.objects.filter(
                    statut=DefiUtilisateur.Statut.TERMINE
                ).count(),
                'soumissions_total': soumissions.count(),
                'soumissions_en_attente': soumissions.filter(
                    statut=SoumissionActivite.Statut.EN_ATTENTE
                ).count(),
                'soumissions_validees': validees.count(),
                'soumissions_refusees': soumissions.filter(
                    statut=SoumissionActivite.Statut.REFUSEE
                ).count(),
                'personnes_sensibilisees': validees.aggregate(
                    total=Sum('nombre_personnes_sensibilisees')
                )['total'] or 0,
                'points_attribues': Validation.objects.filter(
                    decision=Validation.Decision.ACCEPTEE,
                    points_appliques=True,
                ).aggregate(total=Sum('points_attribues'))['total'] or 0,
            }
            return reponse_succes('statistiques', statistiques)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)