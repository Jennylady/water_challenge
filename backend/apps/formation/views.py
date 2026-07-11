from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.formation.models import (
    Module,
    IllustrationModule,
    ProgressionModule,
    Quiz,
    Question,
    Choix,
    TentativeQuiz,
    ReponseQuiz,
)
from apps.formation.serializers import (
    ModuleListeSerializer,
    ModuleDetailSerializer,
    ModuleAdminSerializer,
    IllustrationModuleSerializer,
    QuizAmbassadeurSerializer,
    QuizAdminSerializer,
    TentativeQuizSerializer,
    ParticipantModuleSerializer,
)
from apps.formation.swaggers import (
    swagger_liste_modules_ambassadeur,
    swagger_detail_module_ambassadeur,
    swagger_quiz_module_ambassadeur,
    swagger_soumettre_quiz,
    swagger_historique_tentatives,
    swagger_classement_module,
    swagger_liste_modules_admin,
    swagger_creer_module_admin,
    swagger_modifier_module_admin,
    swagger_supprimer_module_admin,
    swagger_ouvrir_module_admin,
    swagger_fermer_module_admin,
    swagger_participants_module_admin,
    swagger_ajouter_illustration_admin,
    swagger_supprimer_illustration_admin,
    swagger_creer_quiz_admin,
    swagger_detail_quiz_admin,
    swagger_modifier_quiz_admin,
    swagger_supprimer_quiz_admin,
)
from apps.accounts.user.permissions import IsModeratorUser
from apps.accounts.user.models import Profile


POINTS_GAMIFICATION_PAR_MODULE_REUSSI = 20


# ===========================================================================
# Helpers - enveloppe de réponse uniforme {success, message|erreur, <nom>: ...}
# ===========================================================================

def reponse_succes(nom_attribut, valeur, message=None, http_status=status.HTTP_200_OK):
    payload = {'success': True}
    if message:
        payload['message'] = message
    payload[nom_attribut] = valeur
    return Response(payload, status=http_status)


def reponse_erreur(message, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({'success': False, 'erreur': message}, status=http_status)


def module_publie_ou_404(module_id, admin=False):
    if admin:
        return Module.objects.filter(id=module_id).first()
    return Module.objects.filter(id=module_id, est_publie=True).first()


# ===========================================================================
# AMBASSADEUR
# ===========================================================================

class ListeModulesAmbassadeurView(APIView):
    """Liste des modules de formation publiés, avec la progression de l'utilisateur."""
    permission_classes = [IsAuthenticated]

    @swagger_liste_modules_ambassadeur
    def get(self, request):
        try:
            utilisateur = request.user
            modules = Module.objects.filter(est_publie=True)

            niveau = request.query_params.get('niveau')
            if niveau:
                modules = modules.filter(niveau=niveau)

            serializer = ModuleListeSerializer(
                modules, many=True,
                context={'request': request, 'utilisateur': utilisateur},
            )
            return reponse_succes('modules', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetailModuleAmbassadeurView(APIView):
    """
    Détail d'un module. Marque automatiquement le module comme lu pour
    l'utilisateur connecté (si le module est accessible), ce qui débloque le quiz.
    """
    permission_classes = [IsAuthenticated]

    @swagger_detail_module_ambassadeur
    def get(self, request, module_id):
        try:
            utilisateur = request.user
            module = module_publie_ou_404(module_id)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            if not module.est_accessible:
                return reponse_erreur(
                    "Ce module est actuellement fermé (fermeture manuelle ou hors période d'ouverture).",
                    status.HTTP_403_FORBIDDEN,
                )

            progression, _ = ProgressionModule.objects.get_or_create(
                utilisateur_id=utilisateur.id, module=module,
            )
            if not progression.est_lu:
                progression.est_lu = True
                progression.lu_le = timezone.now()
                progression.save(update_fields=['est_lu', 'lu_le'])

            serializer = ModuleDetailSerializer(
                module, context={'request': request, 'progression': progression},
            )
            return reponse_succes('module', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizModuleAmbassadeurView(APIView):
    """Récupère le quiz d'un module (sans les bonnes réponses), débloqué après lecture."""
    permission_classes = [IsAuthenticated]

    @swagger_quiz_module_ambassadeur
    def get(self, request, module_id):
        try:
            utilisateur = request.user
            module = module_publie_ou_404(module_id)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            quiz = getattr(module, 'quiz', None)
            if quiz is None:
                return reponse_erreur("Ce module n'a pas de quiz.", status.HTTP_404_NOT_FOUND)

            if not module.est_accessible:
                return reponse_erreur('Ce module est actuellement fermé.', status.HTTP_403_FORBIDDEN)

            progression = ProgressionModule.objects.filter(
                utilisateur_id=utilisateur.id, module=module,
            ).first()
            if progression is None or not progression.est_lu:
                return reponse_erreur(
                    "Vous devez d'abord lire le module avant d'accéder au quiz.",
                    status.HTTP_403_FORBIDDEN,
                )

            serializer = QuizAmbassadeurSerializer(quiz)
            return reponse_succes('quiz', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class SoumettreQuizAmbassadeurView(APIView):
    """
    Soumet les réponses d'un utilisateur à un quiz. Scoring 100% automatique en fin
    de quiz : gère choix_unique, choix_multiple, et reponse_courte, avec points par
    question. Met à jour la progression du module et les points de gamification.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_soumettre_quiz
    def post(self, request, module_id):
        try:
            utilisateur = request.user
            module = module_publie_ou_404(module_id)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            quiz = getattr(module, 'quiz', None)
            if quiz is None:
                return reponse_erreur("Ce module n'a pas de quiz.", status.HTTP_404_NOT_FOUND)

            if not module.est_accessible:
                return reponse_erreur(
                    'Ce module est actuellement fermé, impossible de soumettre le quiz.',
                    status.HTTP_403_FORBIDDEN,
                )

            progression = ProgressionModule.objects.filter(
                utilisateur_id=utilisateur.id, module=module,
            ).first()
            if progression is None or not progression.est_lu:
                return reponse_erreur(
                    "Vous devez d'abord lire le module avant de soumettre le quiz.",
                    status.HTTP_403_FORBIDDEN,
                )

            reponses_payload = request.data.get('reponses')
            if not isinstance(reponses_payload, list) or not reponses_payload:
                return reponse_erreur(
                    "Le champ 'reponses' est requis et doit être une liste non vide.",
                    status.HTTP_400_BAD_REQUEST,
                )

            questions = list(quiz.questions.all())
            if not questions:
                return reponse_erreur("Ce quiz n'a aucune question.", status.HTTP_400_BAD_REQUEST)

            questions_par_id = {q.id: q for q in questions}
            reponses_par_question_id = {}
            for item in reponses_payload:
                question_id = item.get('question_id')
                if question_id is None:
                    return reponse_erreur(
                        "Chaque réponse doit contenir 'question_id'.", status.HTTP_400_BAD_REQUEST
                    )
                question_id = int(question_id)
                if question_id not in questions_par_id:
                    return reponse_erreur(
                        f"La question {question_id} n'appartient pas à ce quiz.",
                        status.HTTP_400_BAD_REQUEST,
                    )
                reponses_par_question_id[question_id] = item

            points_total = sum(q.points for q in questions)
            points_obtenus = 0
            corrections = []  # liste de (question, est_correcte, points, choix_ids, reponse_texte)

            for question in questions:
                item = reponses_par_question_id.get(question.id)
                if item is None:
                    corrections.append((question, False, 0, [], None))
                    continue

                if question.type_question == Question.TypeQuestion.REPONSE_COURTE:
                    reponse_texte = (item.get('reponse_texte') or '').strip()
                    reponses_valides = question.reponses_acceptees or []
                    if question.sensible_a_la_casse:
                        est_correcte = reponse_texte in reponses_valides
                    else:
                        reponse_normalisee = reponse_texte.lower()
                        est_correcte = reponse_normalisee in [str(r).lower() for r in reponses_valides]
                    points = question.points if est_correcte else 0
                    corrections.append((question, est_correcte, points, [], reponse_texte))

                else:
                    choix_ids = item.get('choix_ids')
                    if not isinstance(choix_ids, list) or not choix_ids:
                        return reponse_erreur(
                            f"La question {question.id} nécessite une liste 'choix_ids' non vide.",
                            status.HTTP_400_BAD_REQUEST,
                        )
                    if question.type_question == Question.TypeQuestion.CHOIX_UNIQUE and len(choix_ids) != 1:
                        return reponse_erreur(
                            f"La question {question.id} est à choix unique : un seul 'choix_id' attendu.",
                            status.HTTP_400_BAD_REQUEST,
                        )

                    choix_ids = [int(c) for c in choix_ids]
                    choix_valides = list(Choix.objects.filter(id__in=choix_ids, question=question))
                    if len(choix_valides) != len(set(choix_ids)):
                        return reponse_erreur(
                            f"Un ou plusieurs choix ne correspondent pas à la question {question.id}.",
                            status.HTTP_400_BAD_REQUEST,
                        )

                    ids_corrects = set(
                        question.choix.filter(est_correct=True).values_list('id', flat=True)
                    )
                    ids_selectionnes = set(choix_ids)
                    est_correcte = ids_selectionnes == ids_corrects
                    points = question.points if est_correcte else 0
                    corrections.append((question, est_correcte, points, choix_ids, None))

                points_obtenus += corrections[-1][2]

            score = round((points_obtenus / points_total) * 100) if points_total > 0 else 0
            est_reussi = score >= quiz.score_de_reussite

            with transaction.atomic():
                tentative = TentativeQuiz.objects.create(
                    utilisateur_id=utilisateur.id,
                    quiz=quiz,
                    score=score,
                    points_obtenus=points_obtenus,
                    points_total=points_total,
                    est_reussi=est_reussi,
                )
                for question, est_correcte, points, choix_ids, reponse_texte in corrections:
                    reponse = ReponseQuiz.objects.create(
                        tentative=tentative,
                        question=question,
                        reponse_texte=reponse_texte,
                        est_correcte=est_correcte,
                        points_obtenus=points,
                    )
                    if choix_ids:
                        reponse.choix_selectionnes.set(choix_ids)

                if est_reussi and not progression.est_termine:
                    progression.est_termine = True
                    progression.termine_le = timezone.now()
                    progression.save(update_fields=['est_termine', 'termine_le'])

                    profile = Profile.objects.filter(user_id=utilisateur.id).first()
                    if profile is not None:
                        profile.points = profile.points + POINTS_GAMIFICATION_PAR_MODULE_REUSSI
                        profile.save(update_fields=['points'])
                        profile.update_level()

            serializer = TentativeQuizSerializer(tentative)
            message = 'Quiz réussi !' if est_reussi else 'Quiz terminé, score insuffisant pour valider.'
            return reponse_succes('tentative', serializer.data, message=message, http_status=status.HTTP_201_CREATED)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class HistoriqueTentativesAmbassadeurView(APIView):
    """Historique des tentatives de quiz de l'utilisateur connecté, pour un module donné."""
    permission_classes = [IsAuthenticated]

    @swagger_historique_tentatives
    def get(self, request, module_id):
        try:
            utilisateur = request.user
            module = module_publie_ou_404(module_id)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            quiz = getattr(module, 'quiz', None)
            if quiz is None:
                return reponse_erreur("Ce module n'a pas de quiz.", status.HTTP_404_NOT_FOUND)

            tentatives = TentativeQuiz.objects.filter(
                utilisateur_id=utilisateur.id, quiz=quiz,
            ).order_by('-cree_le')

            serializer = TentativeQuizSerializer(tentatives, many=True)
            return reponse_succes('tentatives', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClassementModuleView(APIView):
    """Classement (leaderboard) des participants d'un module, basé sur leur meilleur score."""
    permission_classes = [IsAuthenticated]

    @swagger_classement_module
    def get(self, request, module_id):
        try:
            module = module_publie_ou_404(module_id)
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            quiz = getattr(module, 'quiz', None)
            if quiz is None:
                return reponse_erreur("Ce module n'a pas de quiz.", status.HTTP_404_NOT_FOUND)

            classement = _construire_classement(quiz)
            return reponse_succes('classement', classement)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


def _construire_classement(quiz):
    """Construit le classement : meilleure tentative par utilisateur, triée par score puis rapidité."""
    meilleures_par_utilisateur = {}
    for tentative in TentativeQuiz.objects.filter(quiz=quiz).select_related('utilisateur').order_by('cree_le'):
        courante = meilleures_par_utilisateur.get(tentative.utilisateur_id)
        if courante is None or tentative.points_obtenus > courante.points_obtenus:
            meilleures_par_utilisateur[tentative.utilisateur_id] = tentative

    nb_tentatives_par_utilisateur = {}
    for tentative in TentativeQuiz.objects.filter(quiz=quiz).values_list('utilisateur_id', flat=True):
        nb_tentatives_par_utilisateur[tentative] = nb_tentatives_par_utilisateur.get(tentative, 0) + 1

    lignes = sorted(
        meilleures_par_utilisateur.values(),
        key=lambda t: (-t.points_obtenus, t.cree_le),
    )

    classement = []
    for rang, tentative in enumerate(lignes, start=1):
        utilisateur = tentative.utilisateur
        classement.append({
            'rang': rang,
            'utilisateur_id': utilisateur.id,
            'utilisateur_nom': getattr(utilisateur, 'full_name', str(utilisateur)),
            'meilleur_score': tentative.score,
            'meilleurs_points': tentative.points_obtenus,
            'est_reussi': tentative.est_reussi,
            'tentatives_effectuees': nb_tentatives_par_utilisateur.get(utilisateur.id, 0),
            'terminee_le': tentative.cree_le,
        })
    return classement


# ===========================================================================
# ADMIN - Modules
# ===========================================================================

class ListeModulesAdminView(APIView):
    """[Admin] Liste tous les modules, publiés ou non."""
    permission_classes = [IsAuthenticated, IsModeratorUser]

    @swagger_liste_modules_admin
    def get(self, request):
        try:
            modules = Module.objects.all()

            niveau = request.query_params.get('niveau')
            if niveau:
                modules = modules.filter(niveau=niveau)

            est_publie = request.query_params.get('est_publie')
            if est_publie is not None:
                modules = modules.filter(est_publie=est_publie.lower() in ('true', '1'))

            serializer = ModuleAdminSerializer(modules, many=True, context={'request': request})
            return reponse_succes('modules', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreerModuleAdminView(APIView):
    """[Admin] Crée un module de formation (multipart, image de couverture facultative)."""
    permission_classes = [IsAuthenticated, IsModeratorUser]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_creer_module_admin
    def post(self, request):
        try:
            titre = request.data.get('titre')
            contenu = request.data.get('contenu')
            resume = request.data.get('resume')
            niveau = request.data.get('niveau')

            if not titre or not contenu or not resume or not niveau:
                return reponse_erreur(
                    "Les champs 'titre', 'contenu', 'resume' et 'niveau' sont requis.",
                    status.HTTP_400_BAD_REQUEST,
                )

            from django.utils.text import slugify
            slug_de_base = slugify(titre)
            slug = slug_de_base
            compteur = 1
            while Module.objects.filter(slug=slug).exists():
                slug = f'{slug_de_base}-{compteur}'
                compteur += 1

            module = Module.objects.create(
                titre=titre,
                slug=slug,
                contenu=contenu,
                resume=resume,
                niveau=niveau,
                ordre=int(request.data.get('ordre', 0) or 0),
                est_publie=str(request.data.get('est_publie', 'true')).lower() in ('true', '1'),
                est_ouvert=str(request.data.get('est_ouvert', 'true')).lower() in ('true', '1'),
                date_debut=request.data.get('date_debut') or None,
                date_fin=request.data.get('date_fin') or None,
                url_video=request.data.get('url_video') or None,
                image_couverture=request.FILES.get('image_couverture'),
            )

            serializer = ModuleAdminSerializer(module, context={'request': request})
            return reponse_succes('module', serializer.data, message='Module créé.', http_status=status.HTTP_201_CREATED)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModifierModuleAdminView(APIView):
    """[Admin] Modifie un module de formation existant (multipart)."""
    permission_classes = [IsAuthenticated, IsModeratorUser]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_modifier_module_admin
    def put(self, request, module_id):
        try:
            module = Module.objects.filter(id=module_id).first()
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            champs_texte = ['titre', 'contenu', 'resume', 'niveau', 'url_video']
            for champ in champs_texte:
                if champ in request.data:
                    setattr(module, champ, request.data.get(champ) or None)

            if 'ordre' in request.data:
                module.ordre = int(request.data.get('ordre') or 0)
            if 'est_publie' in request.data:
                module.est_publie = str(request.data.get('est_publie')).lower() in ('true', '1')
            if 'est_ouvert' in request.data:
                module.est_ouvert = str(request.data.get('est_ouvert')).lower() in ('true', '1')
            if 'date_debut' in request.data:
                module.date_debut = request.data.get('date_debut') or None
            if 'date_fin' in request.data:
                module.date_fin = request.data.get('date_fin') or None
            if 'image_couverture' in request.FILES:
                module.image_couverture = request.FILES.get('image_couverture')

            module.save()

            serializer = ModuleAdminSerializer(module, context={'request': request})
            return reponse_succes('module', serializer.data, message='Module modifié.')
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class SupprimerModuleAdminView(APIView):
    """[Admin] Supprime un module de formation."""
    permission_classes = [IsAuthenticated, IsModeratorUser]

    @swagger_supprimer_module_admin
    def delete(self, request, module_id):
        try:
            module = Module.objects.filter(id=module_id).first()
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            module.delete()
            return reponse_succes('module', None, message='Module supprimé.', http_status=status.HTTP_200_OK)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class OuvrirModuleAdminView(APIView):
    """[Admin] Ouvre manuellement un module (le rend accessible aux ambassadeurs)."""
    permission_classes = [IsAuthenticated, IsModeratorUser]

    @swagger_ouvrir_module_admin
    def post(self, request, module_id):
        try:
            module = Module.objects.filter(id=module_id).first()
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            module.est_ouvert = True
            module.save(update_fields=['est_ouvert'])
            serializer = ModuleAdminSerializer(module, context={'request': request})
            return reponse_succes('module', serializer.data, message='Module ouvert.')
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class FermerModuleAdminView(APIView):
    """[Admin] Ferme manuellement un module (bloque son accès aux ambassadeurs)."""
    permission_classes = [IsAuthenticated, IsModeratorUser]

    @swagger_fermer_module_admin
    def post(self, request, module_id):
        try:
            module = Module.objects.filter(id=module_id).first()
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)
            module.est_ouvert = False
            module.save(update_fields=['est_ouvert'])
            serializer = ModuleAdminSerializer(module, context={'request': request})
            return reponse_succes('module', serializer.data, message='Module fermé.')
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParticipantsModuleAdminView(APIView):
    """[Admin] Liste des participants d'un module et leur progression."""
    permission_classes = [IsAuthenticated, IsModeratorUser]

    @swagger_participants_module_admin
    def get(self, request, module_id):
        try:
            module = Module.objects.filter(id=module_id).first()
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            participants = module.progressions.select_related('utilisateur').all()
            serializer = ParticipantModuleSerializer(participants, many=True)
            return reponse_succes('participants', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class AjouterIllustrationAdminView(APIView):
    """[Admin] Ajoute une illustration/infographie à un module (multipart)."""
    permission_classes = [IsAuthenticated, IsModeratorUser]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_ajouter_illustration_admin
    def post(self, request, module_id):
        try:
            module = Module.objects.filter(id=module_id).first()
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            image = request.FILES.get('image')
            if not image:
                return reponse_erreur("Le champ 'image' est requis.", status.HTTP_400_BAD_REQUEST)

            illustration = IllustrationModule.objects.create(
                module=module,
                image=image,
                legende=request.data.get('legende') or None,
                ordre=int(request.data.get('ordre', 0) or 0),
            )

            serializer = IllustrationModuleSerializer(illustration, context={'request': request})
            return reponse_succes('illustration', serializer.data, message='Illustration ajoutée.', http_status=status.HTTP_201_CREATED)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class SupprimerIllustrationAdminView(APIView):
    """[Admin] Supprime une illustration de module."""
    permission_classes = [IsAuthenticated, IsModeratorUser]

    @swagger_supprimer_illustration_admin
    def delete(self, request, illustration_id):
        try:
            illustration = IllustrationModule.objects.filter(id=illustration_id).first()
            if illustration is None:
                return reponse_erreur('Illustration introuvable.', status.HTTP_404_NOT_FOUND)
            illustration.delete()
            return reponse_succes('illustration', None, message='Illustration supprimée.')
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===========================================================================
# ADMIN - Quiz
# ===========================================================================

class CreerQuizAdminView(APIView):
    """
    [Admin] Crée le quiz d'un module, avec ses questions et choix imbriqués (JSON).
    Supporte les types choix_unique, choix_multiple, reponse_courte, avec points par question.
    """
    permission_classes = [IsAuthenticated, IsModeratorUser]
    parser_classes = [JSONParser]

    @swagger_creer_quiz_admin
    def post(self, request, module_id):
        try:
            module = Module.objects.filter(id=module_id).first()
            if module is None:
                return reponse_erreur('Module introuvable.', status.HTTP_404_NOT_FOUND)

            if hasattr(module, 'quiz'):
                return reponse_erreur(
                    'Ce module possède déjà un quiz. Modifiez-le plutôt.', status.HTTP_400_BAD_REQUEST
                )

            titre = request.data.get('titre')
            questions_payload = request.data.get('questions')

            if not titre or not isinstance(questions_payload, list) or not questions_payload:
                return reponse_erreur(
                    "Les champs 'titre' et 'questions' (liste non vide) sont requis.",
                    status.HTTP_400_BAD_REQUEST,
                )

            types_valides = {c[0] for c in Question.TypeQuestion.choices}

            with transaction.atomic():
                quiz = Quiz.objects.create(
                    module=module,
                    titre=titre,
                    score_de_reussite=int(request.data.get('score_de_reussite', 50) or 50),
                )

                for ordre_question, question_data in enumerate(questions_payload):
                    texte_question = question_data.get('texte')
                    type_question = question_data.get('type_question', Question.TypeQuestion.CHOIX_UNIQUE)
                    if not texte_question:
                        raise ValueError('Chaque question doit avoir un texte.')
                    if type_question not in types_valides:
                        raise ValueError(f"Type de question invalide : '{type_question}'.")

                    question = Question.objects.create(
                        quiz=quiz,
                        texte=texte_question,
                        type_question=type_question,
                        points=int(question_data.get('points', 1) or 1),
                        ordre=question_data.get('ordre', ordre_question),
                        reponses_acceptees=question_data.get('reponses_acceptees', []) or [],
                        sensible_a_la_casse=bool(question_data.get('sensible_a_la_casse', False)),
                    )

                    if type_question == Question.TypeQuestion.REPONSE_COURTE:
                        if not question.reponses_acceptees:
                            raise ValueError(
                                f"La question '{texte_question}' (réponse courte) doit avoir des "
                                "'reponses_acceptees' non vides."
                            )
                    else:
                        choix_payload = question_data.get('choix')
                        if not isinstance(choix_payload, list) or not choix_payload:
                            raise ValueError(
                                f"La question '{texte_question}' doit avoir une liste 'choix' non vide."
                            )
                        if not any(c.get('est_correct') for c in choix_payload):
                            raise ValueError(
                                f"La question '{texte_question}' doit avoir au moins un choix correct."
                            )
                        if type_question == Question.TypeQuestion.CHOIX_UNIQUE:
                            nb_corrects = sum(1 for c in choix_payload if c.get('est_correct'))
                            if nb_corrects != 1:
                                raise ValueError(
                                    f"La question '{texte_question}' est à choix unique : "
                                    "exactement un choix correct est attendu."
                                )
                        for choix_data in choix_payload:
                            Choix.objects.create(
                                question=question,
                                texte=choix_data.get('texte'),
                                est_correct=bool(choix_data.get('est_correct', False)),
                                explication=choix_data.get('explication') or None,
                            )

            serializer = QuizAdminSerializer(quiz)
            return reponse_succes('quiz', serializer.data, message='Quiz créé.', http_status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return reponse_erreur(str(exc), status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetailQuizAdminView(APIView):
    """[Admin] Détail complet d'un quiz, avec les bonnes réponses."""
    permission_classes = [IsAuthenticated, IsModeratorUser]

    @swagger_detail_quiz_admin
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.filter(id=quiz_id).first()
            if quiz is None:
                return reponse_erreur('Quiz introuvable.', status.HTTP_404_NOT_FOUND)
            serializer = QuizAdminSerializer(quiz)
            return reponse_succes('quiz', serializer.data)
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModifierQuizAdminView(APIView):
    """[Admin] Modifie le titre / score de réussite d'un quiz."""
    permission_classes = [IsAuthenticated, IsModeratorUser]
    parser_classes = [JSONParser]

    @swagger_modifier_quiz_admin
    def put(self, request, quiz_id):
        try:
            quiz = Quiz.objects.filter(id=quiz_id).first()
            if quiz is None:
                return reponse_erreur('Quiz introuvable.', status.HTTP_404_NOT_FOUND)

            if 'titre' in request.data:
                quiz.titre = request.data.get('titre')
            if 'score_de_reussite' in request.data:
                quiz.score_de_reussite = int(request.data.get('score_de_reussite'))
            quiz.save()

            serializer = QuizAdminSerializer(quiz)
            return reponse_succes('quiz', serializer.data, message='Quiz modifié.')
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class SupprimerQuizAdminView(APIView):
    """[Admin] Supprime un quiz (et ses questions/choix en cascade)."""
    permission_classes = [IsAuthenticated, IsModeratorUser]

    @swagger_supprimer_quiz_admin
    def delete(self, request, quiz_id):
        try:
            quiz = Quiz.objects.filter(id=quiz_id).first()
            if quiz is None:
                return reponse_erreur('Quiz introuvable.', status.HTTP_404_NOT_FOUND)
            quiz.delete()
            return reponse_succes('quiz', None, message='Quiz supprimé.')
        except Exception as exc:
            return reponse_erreur(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)