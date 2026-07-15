import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.user.permissions import IsModeratorUser

from .models import (
    Choix, IllustrationModule,
    ImageIllustrationModule, RessourceModule, Module, ProgressionModule, Question, Quiz, TentativeQuiz,
)
from .serializers import (
    IllustrationModuleSerializer, RessourceModuleSerializer,
    ModuleAdminSerializer, ModuleDetailSerializer, ModuleListeSerializer, ParticipantModuleSerializer,
    QuestionAdminSerializer, QuizAdminSerializer, QuizAmbassadeurSerializer, TentativeQuizSerializer,
)
from .services import (
    ErreurQuiz, charger_progressions_utilisateur,
    demarrer_ou_reprendre_tentative, enregistrer_reponse, soumettre_tentative,
)
from .utils import (
    _creer_question,_datetime_ou_none,_erreur_interne,_modifier_question,_module_admin,_module_ambassadeur,
    _question_admin,_quiz_admin,_valider_configuration_question,_slug_unique,_valider_type_question,
    reponse_erreur,reponse_succes,_int,_bool
)
from .swaggers import (
    swagger_ajouter_illustration_admin, swagger_ajouter_questions_banque_admin,
    swagger_ajouter_ressources_admin, swagger_classement_module, swagger_creer_module_admin, swagger_creer_quiz_admin,
    swagger_detail_module_ambassadeur, swagger_detail_quiz_admin, swagger_fermer_module_admin, swagger_historique_tentatives, 
    swagger_liste_modules_admin, swagger_liste_modules_ambassadeur, swagger_ma_progression_formation, swagger_marquer_module_lu,
    swagger_modifier_module_admin, swagger_modifier_question_admin, swagger_modifier_quiz_admin,
    swagger_ouvrir_module_admin, swagger_participants_module_admin, swagger_quiz_module_ambassadeur,
    swagger_repondre_question, swagger_soumettre_tentative, swagger_supprimer_illustration_admin, swagger_supprimer_module_admin,
    swagger_supprimer_question_admin, swagger_supprimer_ressource_admin, swagger_supprimer_quiz_admin,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Ambassadeur
# =============================================================================

class ListeModulesAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_liste_modules_ambassadeur
    def get(self, request):
        try:
            modules = Module.objects.filter(est_publie=True)
            niveau = request.query_params.get('niveau')
            if niveau:
                modules = modules.filter(niveau=niveau)
            modules = list(modules)
            progressions = charger_progressions_utilisateur(request.user, modules)
            serializer = ModuleListeSerializer(
                modules,
                many=True,
                context={
                    'request': request,
                    'utilisateur': request.user,
                    'progressions': progressions,
                },
            )
            return reponse_succes('modules', serializer.data)
        except Exception as exc:
            return _erreur_interne(exc)


class DetailModuleAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_detail_module_ambassadeur
    def get(self, request, module_slug):
        try:
            module = _module_ambassadeur(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            if not module.est_accessible:
                return reponse_erreur('Ce module est actuellement fermé.', status.HTTP_403_FORBIDDEN)

            progression = charger_progressions_utilisateur(
                request.user, [module]
            ).get(module.id)
            serializer = ModuleDetailSerializer(
                module,
                context={'request': request, 'progression': progression},
            )
            return reponse_succes('module', serializer.data)
        except Exception as exc:
            return _erreur_interne(exc)


class QuizModuleAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_quiz_module_ambassadeur
    def get(self, request, module_slug):
        try:
            module = _module_ambassadeur(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            if not module.est_accessible:
                return reponse_erreur('Ce module est actuellement fermé.', status.HTTP_403_FORBIDDEN)

            quiz = getattr(module, 'quiz', None)
            if quiz is None:
                return reponse_erreur("Ce module n'a pas de quiz.", status.HTTP_404_NOT_FOUND)

            tentative, creee = demarrer_ou_reprendre_tentative(request.user, quiz)
            serializer = QuizAmbassadeurSerializer(
                quiz, context={'tentative': tentative}
            )
            message = 'Nouvelle tentative créée.' if creee else 'Tentative en cours reprise.'
            return reponse_succes('quiz', serializer.data, message=message)
        except ErreurQuiz as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class RepondreQuestionAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [JSONParser]

    @swagger_repondre_question
    def post(self, request, tentative_id, question_id):
        try:
            tentative = TentativeQuiz.objects.select_related('quiz').filter(
                uuid=tentative_id, utilisateur=request.user
            ).first()
            if tentative is None:
                return reponse_erreur('Tentative introuvable.', status.HTTP_404_NOT_FOUND)
            question = Question.objects.filter(
                uuid=question_id, quiz=tentative.quiz
            ).first()
            if question is None:
                return reponse_erreur('Question introuvable.', status.HTTP_404_NOT_FOUND)

            reponse, resultat = enregistrer_reponse(
                tentative=tentative,
                question=question,
                choix_ids=request.data.get('choix_ids'),
                reponse_texte=request.data.get('reponse_texte'),
            )
            donnees = {
                'id': reponse.uuid,
                'question_id': question.uuid,
                'enregistree': True,
                'modifiee_le': reponse.modifiee_le,
            }
            if tentative.quiz.correction_automatique:
                donnees['est_correcte'] = resultat.est_correcte
                if not resultat.est_correcte:
                    donnees['correction'] = resultat.correction
                    if resultat.explication:
                        donnees['explication'] = resultat.explication

            return reponse_succes(
                'reponse', donnees, message='Réponse enregistrée avec succès.'
            )
        except (ErreurQuiz, DjangoValidationError, ValueError) as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class SoumettreTentativeQuizAmbassadeurView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [JSONParser]

    @swagger_soumettre_tentative
    def post(self, request, tentative_id):
        try:
            tentative = TentativeQuiz.objects.filter(
                uuid=tentative_id, utilisateur=request.user
            ).first()
            if tentative is None:
                return reponse_erreur('Tentative introuvable.', status.HTTP_404_NOT_FOUND)
            tentative = soumettre_tentative(
                tentative=tentative, utilisateur=request.user
            )
            serializer = TentativeQuizSerializer(tentative)
            message = (
                'Quiz réussi !' if tentative.est_reussi
                else 'Quiz soumis, mais le score est insuffisant.'
            )
            return reponse_succes('tentative', serializer.data, message=message)
        except ErreurQuiz as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class HistoriqueTentativesAmbassadeurView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_historique_tentatives
    def get(self, request, module_slug):
        try:
            module = _module_ambassadeur(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            quiz = getattr(module, 'quiz', None)
            if quiz is None:
                return reponse_erreur("Ce module n'a pas de quiz.", status.HTTP_404_NOT_FOUND)
            tentatives = TentativeQuiz.objects.filter(
                utilisateur=request.user, quiz=quiz
            ).select_related('quiz', 'quiz__module').order_by('-cree_le')
            serializer = TentativeQuizSerializer(tentatives, many=True)
            return reponse_succes('tentatives', serializer.data)
        except Exception as exc:
            return _erreur_interne(exc)


class ClassementModuleView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_classement_module
    def get(self, request, module_slug):
        try:
            module = _module_ambassadeur(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            quiz = getattr(module, 'quiz', None)
            if quiz is None:
                return reponse_erreur("Ce module n'a pas de quiz.", status.HTTP_404_NOT_FOUND)
            return reponse_succes('classement', _construire_classement(quiz))
        except Exception as exc:
            return _erreur_interne(exc)


def _construire_classement(quiz):
    meilleures = {}
    tentatives = TentativeQuiz.objects.filter(
        quiz=quiz, statut=TentativeQuiz.Statut.SOUMISE
    ).select_related('utilisateur').order_by('soumise_le')
    compte = {}
    for tentative in tentatives:
        compte[tentative.utilisateur_id] = compte.get(tentative.utilisateur_id, 0) + 1
        courante = meilleures.get(tentative.utilisateur_id)
        if courante is None or (
            tentative.score,
            tentative.points_obtenus,
            -(tentative.soumise_le or tentative.cree_le).timestamp(),
        ) > (
            courante.score,
            courante.points_obtenus,
            -(courante.soumise_le or courante.cree_le).timestamp(),
        ):
            meilleures[tentative.utilisateur_id] = tentative

    lignes = sorted(
        meilleures.values(),
        key=lambda t: (-t.score, -t.points_obtenus, t.soumise_le or t.cree_le),
    )
    return [
        {
            'rang': rang,
            'utilisateur_id': tentative.utilisateur_id,
            'utilisateur_nom': getattr(tentative.utilisateur, 'full_name', None)
            or str(tentative.utilisateur),
            'meilleur_score': tentative.score,
            'meilleurs_points': tentative.points_obtenus,
            'est_reussi': tentative.est_reussi,
            'tentatives_effectuees': compte[tentative.utilisateur_id],
            'terminee_le': tentative.soumise_le,
        }
        for rang, tentative in enumerate(lignes, start=1)
    ]


class MarquerModuleLuView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_marquer_module_lu
    def post(self, request, module_slug):
        try:
            module = _module_ambassadeur(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            progression, _ = ProgressionModule.objects.get_or_create(
                utilisateur=request.user,
                module=module,
            )
            if not progression.est_lu:
                progression.est_lu = True
                progression.lu_le = timezone.now()
                progression.save(update_fields=['est_lu', 'lu_le'])

            from apps.recompenses.services import synchroniser_progression_module
            progression = synchroniser_progression_module(request.user, module)
            return reponse_succes(
                'progression',
                {
                    'module_slug': module.slug,
                    'pourcentage': progression.pourcentage,
                    **progression.details_progression,
                    'est_termine': progression.est_termine,
                },
                message='Lecture du module enregistrée.',
            )
        except Exception as exc:
            return _erreur_interne(exc)


class MaProgressionFormationView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_ma_progression_formation
    def get(self, request):
        try:
            modules = list(Module.objects.filter(est_publie=True))
            progressions = charger_progressions_utilisateur(request.user, modules)
            donnees = ModuleListeSerializer(
                modules,
                many=True,
                context={
                    'request': request,
                    'utilisateur': request.user,
                    'progressions': progressions,
                },
            ).data
            total = len(donnees)
            moyenne = (
                round(
                    sum(item['progression']['pourcentage'] for item in donnees) / total
                )
                if total
                else 0
            )
            return reponse_succes(
                'progression',
                {'pourcentage_global': moyenne, 'modules': donnees},
            )
        except Exception as exc:
            return _erreur_interne(exc)


# =============================================================================
# Admin - modules
# =============================================================================

class ListeModulesAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_liste_modules_admin
    def get(self, request):
        try:
            modules = Module.objects.all()
            niveau = request.query_params.get('niveau')
            if niveau:
                modules = modules.filter(niveau=niveau)
            est_publie = request.query_params.get('est_publie')
            if est_publie is not None:
                modules = modules.filter(est_publie=_bool(est_publie))
            serializer = ModuleAdminSerializer(
                modules, many=True, context={'request': request}
            )
            return reponse_succes('modules', serializer.data)
        except Exception as exc:
            return _erreur_interne(exc)


class CreerModuleAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @swagger_creer_module_admin
    def post(self, request):
        try:
            for champ in ['titre', 'contenu', 'resume', 'niveau']:
                if not request.data.get(champ):
                    return reponse_erreur(f"Le champ '{champ}' est requis.")
            titre = str(request.data.get('titre')).strip()
            module = Module(
                titre=titre,
                slug=_slug_unique(titre),
                contenu=str(request.data.get('contenu')).strip(),
                resume=str(request.data.get('resume')).strip(),
                niveau=request.data.get('niveau'),
                ordre=_int(request.data.get('ordre', 0), minimum=0, nom='ordre'),
                est_publie=_bool(request.data.get('est_publie'), True),
                est_ouvert=_bool(request.data.get('est_ouvert'), True),
                date_debut=_datetime_ou_none(request.data.get('date_debut'), 'date_debut'),
                date_fin=_datetime_ou_none(request.data.get('date_fin'), 'date_fin'),
                video=request.FILES.get('video'),
                image_couverture=request.FILES.get('image_couverture'),
            )
            module.full_clean()
            module.save()
            return reponse_succes(
                'module',
                ModuleAdminSerializer(module, context={'request': request}).data,
                message='Module créé.',
                http_status=status.HTTP_201_CREATED,
            )
        except (ErreurQuiz, DjangoValidationError) as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class ModifierModuleAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @swagger_modifier_module_admin
    def put(self, request, module_slug):
        try:
            module = _module_admin(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            for champ in ['titre', 'contenu', 'resume', 'niveau']:
                if champ in request.data:
                    valeur = request.data.get(champ)
                    if not valeur:
                        return reponse_erreur(f"Le champ '{champ}' ne peut pas être vide.")
                    setattr(module, champ, valeur)
            if 'titre' in request.data:
                module.slug = _slug_unique(module.titre, module)
            if 'ordre' in request.data:
                module.ordre = _int(request.data.get('ordre'), minimum=0, nom='ordre')
            if 'est_publie' in request.data:
                module.est_publie = _bool(request.data.get('est_publie'))
            if 'est_ouvert' in request.data:
                module.est_ouvert = _bool(request.data.get('est_ouvert'))
            if 'date_debut' in request.data:
                module.date_debut = _datetime_ou_none(request.data.get('date_debut'), 'date_debut')
            if 'date_fin' in request.data:
                module.date_fin = _datetime_ou_none(request.data.get('date_fin'), 'date_fin')
            if _bool(request.data.get('supprimer_video')):
                module.video = None
            elif 'video' in request.FILES:
                module.video = request.FILES.get('video')

            if _bool(request.data.get('supprimer_image_couverture')):
                module.image_couverture = None
            elif 'image_couverture' in request.FILES:
                module.image_couverture = request.FILES.get('image_couverture')

            module.full_clean()
            module.save()
            return reponse_succes(
                'module',
                ModuleAdminSerializer(module, context={'request': request}).data,
                message='Module modifié.',
            )
        except (ErreurQuiz, DjangoValidationError) as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class SupprimerModuleAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_supprimer_module_admin
    def delete(self, request, module_slug):
        try:
            module = _module_admin(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            module.delete()
            return reponse_succes('module', None, message='Module supprimé.')
        except Exception as exc:
            return _erreur_interne(exc)


class OuvrirModuleAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_ouvrir_module_admin
    def post(self, request, module_slug):
        try:
            module = _module_admin(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            module.est_ouvert = True
            module.save(update_fields=['est_ouvert'])
            return reponse_succes(
                'module', ModuleAdminSerializer(module, context={'request': request}).data,
                message='Module ouvert.',
            )
        except Exception as exc:
            return _erreur_interne(exc)


class FermerModuleAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_fermer_module_admin
    def post(self, request, module_slug):
        try:
            module = _module_admin(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            module.est_ouvert = False
            module.save(update_fields=['est_ouvert'])
            return reponse_succes(
                'module', ModuleAdminSerializer(module, context={'request': request}).data,
                message='Module fermé.',
            )
        except Exception as exc:
            return _erreur_interne(exc)


class ParticipantsModuleAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_participants_module_admin
    def get(self, request, module_slug):
        try:
            module = _module_admin(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            participants = module.progressions.select_related('utilisateur')
            return reponse_succes(
                'participants', ParticipantModuleSerializer(participants, many=True).data
            )
        except Exception as exc:
            return _erreur_interne(exc)


class AjouterIllustrationAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @swagger_ajouter_illustration_admin
    def post(self, request, module_slug):
        try:
            module = _module_admin(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            images = request.FILES.getlist('images') or request.FILES.getlist('image')
            titre = (request.data.get('titre') or '').strip()
            if not titre:
                return reponse_erreur("Le champ 'titre' est requis.")
            if not images:
                return reponse_erreur("Au moins une image est requise dans le champ 'images'.")
            with transaction.atomic():
                illustration = IllustrationModule.objects.create(
                    module=module,
                    titre=titre,
                    description=request.data.get('description') or None,
                    ordre=_int(request.data.get('ordre', 0), minimum=0, nom='ordre'),
                )
                ImageIllustrationModule.objects.bulk_create([
                    ImageIllustrationModule(
                        illustration=illustration,
                        image=image,
                        ordre=index,
                    )
                    for index, image in enumerate(images, start=1)
                ])
            return reponse_succes(
                'illustration',
                IllustrationModuleSerializer(
                    illustration, context={'request': request}
                ).data,
                message='Illustration ajoutée.',
                http_status=status.HTTP_201_CREATED,
            )
        except ErreurQuiz as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class SupprimerIllustrationAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_supprimer_illustration_admin
    def delete(self, request, illustration_id):
        try:
            illustration = IllustrationModule.objects.filter(uuid=illustration_id).first()
            if illustration is None:
                return reponse_erreur('Illustration introuvable.', status.HTTP_404_NOT_FOUND)
            illustration.delete()
            return reponse_succes('illustration', None, message='Illustration supprimée.')
        except Exception as exc:
            return _erreur_interne(exc)


class AjouterRessourcesModuleAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @swagger_ajouter_ressources_admin
    def post(self, request, module_slug):
        try:
            module = _module_admin(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            fichiers = request.FILES.getlist('fichiers') or request.FILES.getlist('fichier')
            if not fichiers:
                return reponse_erreur("Au moins un fichier est requis dans le champ 'fichiers'.")
            ressources = [RessourceModule.objects.create(module=module, fichier=f) for f in fichiers]
            return reponse_succes(
                'ressources',
                RessourceModuleSerializer(ressources, many=True, context={'request': request}).data,
                message='Ressource(s) ajoutée(s).',
                http_status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            return _erreur_interne(exc)


class SupprimerRessourceModuleAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_supprimer_ressource_admin
    def delete(self, request, ressource_id):
        try:
            ressource = RessourceModule.objects.filter(pk=ressource_id).first()
            if ressource is None:
                return reponse_erreur('Ressource introuvable.', status.HTTP_404_NOT_FOUND)
            ressource.delete()
            return reponse_succes('ressource', None, message='Ressource supprimée.')
        except Exception as exc:
            return _erreur_interne(exc)


# =============================================================================
# Admin - quiz et banque de questions
# =============================================================================

class CreerQuizAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [JSONParser]

    @swagger_creer_quiz_admin
    def post(self, request, module_slug):
        try:
            module = _module_admin(module_slug)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            if hasattr(module, 'quiz'):
                return reponse_erreur('Ce module possède déjà un quiz.')

            titre = str(request.data.get('titre') or '').strip()
            if not titre:
                return reponse_erreur("Le champ 'titre' est requis.")
            questions = request.data.get('questions', [])
            if not isinstance(questions, list):
                return reponse_erreur("Le champ 'questions' doit être une liste.")
            nombre_questions = _int(
                request.data.get('nombre_questions', 5),
                minimum=1,
                nom='nombre_questions',
            )
            if questions and nombre_questions > len(questions):
                return reponse_erreur(
                    "'nombre_questions' ne peut pas dépasser le nombre de questions "
                    "initialement fournies."
                )

            with transaction.atomic():
                quiz = Quiz.objects.create(
                    module=module,
                    titre=titre,
                    score_de_reussite=_int(
                        request.data.get('score_de_reussite', 50),
                        minimum=0,
                        maximum=100,
                        nom='score_de_reussite',
                    ),
                    nombre_questions=nombre_questions,
                    correction_automatique=_bool(
                        request.data.get('correction_automatique'), True
                    ),
                )
                for index, donnees in enumerate(questions, start=1):
                    _creer_question(quiz, donnees, ordre_defaut=index)

            return reponse_succes(
                'quiz', QuizAdminSerializer(quiz).data,
                message='Quiz et banque de questions créés.',
                http_status=status.HTTP_201_CREATED,
            )
        except (ErreurQuiz, DjangoValidationError) as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class DetailQuizAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_detail_quiz_admin
    def get(self, request, quiz_id):
        try:
            quiz = _quiz_admin(quiz_id)
            if quiz is None:
                return reponse_erreur('Quiz introuvable.', status.HTTP_404_NOT_FOUND)
            return reponse_succes('quiz', QuizAdminSerializer(quiz).data)
        except Exception as exc:
            return _erreur_interne(exc)


class ModifierQuizAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [JSONParser]

    @swagger_modifier_quiz_admin
    def put(self, request, quiz_id):
        try:
            quiz = _quiz_admin(quiz_id)
            if quiz is None:
                return reponse_erreur('Quiz introuvable.', status.HTTP_404_NOT_FOUND)

            if 'questions' in request.data and quiz.tentatives.exists():
                return reponse_erreur(
                    "La banque ne peut pas être remplacée car des tentatives existent. "
                    "Utilisez l'ajout de question pour enrichir la banque.",
                    status.HTTP_409_CONFLICT,
                )

            with transaction.atomic():
                if 'titre' in request.data:
                    titre = str(request.data.get('titre') or '').strip()
                    if not titre:
                        raise ErreurQuiz("Le champ 'titre' ne peut pas être vide.")
                    quiz.titre = titre
                if 'score_de_reussite' in request.data:
                    quiz.score_de_reussite = _int(
                        request.data.get('score_de_reussite'),
                        minimum=0,
                        maximum=100,
                        nom='score_de_reussite',
                    )
                if 'correction_automatique' in request.data:
                    quiz.correction_automatique = _bool(
                        request.data.get('correction_automatique')
                    )

                questions = None
                if 'questions' in request.data:
                    questions = request.data.get('questions')
                    if not isinstance(questions, list):
                        raise ErreurQuiz("Le champ 'questions' doit être une liste.")
                    quiz.questions.all().delete()
                    for index, donnees in enumerate(questions, start=1):
                        _creer_question(quiz, donnees, ordre_defaut=index)

                if 'nombre_questions' in request.data:
                    quiz.nombre_questions = _int(
                        request.data.get('nombre_questions'),
                        minimum=1,
                        nom='nombre_questions',
                    )
                banque_count = quiz.questions.count()
                if banque_count and quiz.nombre_questions > banque_count:
                    raise ErreurQuiz(
                        "'nombre_questions' ne peut pas dépasser le nombre de questions de la banque."
                    )
                quiz.full_clean()
                quiz.save()

            return reponse_succes(
                'quiz', QuizAdminSerializer(quiz).data, message='Quiz modifié.'
            )
        except (ErreurQuiz, DjangoValidationError) as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class SupprimerQuizAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_supprimer_quiz_admin
    def delete(self, request, quiz_id):
        try:
            quiz = _quiz_admin(quiz_id)
            if quiz is None:
                return reponse_erreur('Quiz introuvable.', status.HTTP_404_NOT_FOUND)
            quiz.delete()
            return reponse_succes('quiz', None, message='Quiz supprimé.')
        except Exception as exc:
            return _erreur_interne(exc)


class AjouterQuestionsBanqueAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [JSONParser]

    @swagger_ajouter_questions_banque_admin
    def post(self, request, quiz_id):
        try:
            quiz = _quiz_admin(quiz_id)
            if quiz is None:
                return reponse_erreur('Quiz introuvable.', status.HTTP_404_NOT_FOUND)
            questions = request.data.get('questions')
            if questions is None and request.data.get('texte'):
                questions = [request.data]
            if not isinstance(questions, list) or not questions:
                return reponse_erreur(
                    "Envoyez une liste non vide dans le champ 'questions'."
                )

            depart = quiz.questions.count()
            with transaction.atomic():
                creees = [
                    _creer_question(quiz, donnees, ordre_defaut=depart + index)
                    for index, donnees in enumerate(questions, start=1)
                ]
            return reponse_succes(
                'questions', QuestionAdminSerializer(creees, many=True).data,
                message=f'{len(creees)} question(s) ajoutée(s) à la banque.',
                http_status=status.HTTP_201_CREATED,
            )
        except (ErreurQuiz, DjangoValidationError) as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class ModifierQuestionAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []
    parser_classes = [JSONParser]

    @swagger_modifier_question_admin
    def put(self, request, question_id):
        try:
            question = _question_admin(question_id)
            if question is None:
                return reponse_erreur('Question introuvable.', status.HTTP_404_NOT_FOUND)
            with transaction.atomic():
                question = _modifier_question(question, request.data)
            return reponse_succes(
                'question', QuestionAdminSerializer(question).data,
                message='Question modifiée.',
            )
        except ErreurQuiz as exc:
            code = status.HTTP_409_CONFLICT if 'déjà été utilisée' in str(exc) else status.HTTP_400_BAD_REQUEST
            return reponse_erreur(str(exc), code)
        except (DjangoValidationError, ValueError) as exc:
            return reponse_erreur(str(exc))
        except Exception as exc:
            return _erreur_interne(exc)


class SupprimerQuestionAdminView(APIView):
    permission_classes = [IsModeratorUser]
    authentication_classes = []

    @swagger_supprimer_question_admin
    def delete(self, request, question_id):
        try:
            question = _question_admin(question_id)
            if question is None:
                return reponse_erreur('Question introuvable.', status.HTTP_404_NOT_FOUND)
            if question.tirages.exists() or question.reponses.exists():
                return reponse_erreur(
                    "Cette question a déjà été utilisée et ne peut pas être supprimée. "
                    "Elle doit être conservée pour l'historique.",
                    status.HTTP_409_CONFLICT,
                )
            question.delete()
            return reponse_succes('question', None, message='Question supprimée.')
        except Exception as exc:
            return _erreur_interne(exc)
