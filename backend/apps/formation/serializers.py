from rest_framework import serializers

from .models import (
    Choix,
    IllustrationModule,
    ImageIllustrationModule,
    RessourceModule,
    Module,
    ProgressionModule,
    Question,
    Quiz,
    ReponseQuiz,
    TentativeQuiz,
)


# =============================================================================
# Fichiers de module
# =============================================================================

class ImageIllustrationModuleSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    image = serializers.FileField(read_only=True, use_url=True)

    class Meta:
        model = ImageIllustrationModule
        fields = ['id', 'ordre', 'image']


class IllustrationModuleSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    images = ImageIllustrationModuleSerializer(many=True, read_only=True)

    class Meta:
        model = IllustrationModule
        fields = ['id', 'titre', 'description', 'ordre', 'images']


class RessourceModuleSerializer(serializers.ModelSerializer):
    fichier = serializers.FileField(read_only=True, use_url=True)

    class Meta:
        model = RessourceModule
        fields = ['id', 'fichier']


# =============================================================================
# Choix et questions
# =============================================================================

class ChoixAmbassadeurSerializer(serializers.ModelSerializer):
    """Ne révèle jamais si un choix est correct."""

    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Choix
        fields = ['id', 'texte']


class ChoixAdminSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Choix
        fields = ['id', 'texte', 'est_correct', 'explication']


class QuestionAmbassadeurSerializer(serializers.ModelSerializer):
    """
    Sérialisation publique d'une question tirée.

    - choix unique/multiple : retourne uniquement les choix disponibles ;
    - réponse courte : ne retourne ni choix ni réponse attendue ;
    - aucune correction n'est exposée ici.
    """

    id = serializers.UUIDField(source='uuid', read_only=True)
    ordre = serializers.SerializerMethodField()
    choix = serializers.SerializerMethodField()
    reponse_enregistree = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'texte', 'type_question', 'points', 'ordre',
            'choix', 'reponse_enregistree',
        ]

    def get_ordre(self, obj):
        return self.context.get('ordres', {}).get(obj.pk, obj.ordre)

    def get_choix(self, obj):
        if obj.type_question == Question.TypeQuestion.REPONSE_COURTE:
            return None
        return ChoixAmbassadeurSerializer(obj.choix.all(), many=True).data

    def get_reponse_enregistree(self, obj):
        reponse = self.context.get('reponses', {}).get(obj.pk)
        if reponse is None:
            return None
        if obj.type_question == Question.TypeQuestion.REPONSE_COURTE:
            return {'reponse_texte': reponse.reponse_texte}
        return {'choix_ids': [choix.uuid for choix in reponse.choix_selectionnes.all()]}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.type_question == Question.TypeQuestion.REPONSE_COURTE:
            data.pop('choix', None)
        return data


class QuestionAdminSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    choix = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'texte', 'type_question', 'points', 'ordre', 'explication',
            'choix', 'reponses_acceptees', 'sensible_a_la_casse',
        ]

    def get_choix(self, obj):
        if obj.type_question == Question.TypeQuestion.REPONSE_COURTE:
            return []
        return ChoixAdminSerializer(obj.choix.all(), many=True).data


# =============================================================================
# Quiz
# =============================================================================

class QuizAmbassadeurSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    module_id = serializers.UUIDField(source='module.uuid', read_only=True)
    tentative_id = serializers.SerializerMethodField()
    statut_tentative = serializers.SerializerMethodField()
    questions_repondues = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'module_id', 'titre', 'score_de_reussite',
            'nombre_questions', 'correction_automatique',
            'tentative_id', 'statut_tentative', 'questions_repondues', 'questions',
        ]

    def _tentative(self):
        return self.context['tentative']

    def get_tentative_id(self, obj):
        return self._tentative().uuid

    def get_statut_tentative(self, obj):
        return self._tentative().statut

    def get_questions_repondues(self, obj):
        return self._tentative().reponses.count()

    def get_questions(self, obj):
        tentative = self._tentative()
        tirages = list(
            tentative.questions_selectionnees
            .select_related('question')
            .prefetch_related('question__choix')
            .order_by('ordre')
        )
        questions = [tirage.question for tirage in tirages]
        ordres = {tirage.question_id: tirage.ordre for tirage in tirages}
        reponses = {
            reponse.question_id: reponse
            for reponse in tentative.reponses.prefetch_related('choix_selectionnes')
        }
        return QuestionAmbassadeurSerializer(
            questions,
            many=True,
            context={'ordres': ordres, 'reponses': reponses},
        ).data


class QuizAdminSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    module_id = serializers.UUIDField(source='module.uuid', read_only=True)
    points_total_banque = serializers.IntegerField(read_only=True)
    nombre_questions_banque = serializers.IntegerField(read_only=True)
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'module_id', 'titre', 'score_de_reussite',
            'nombre_questions', 'correction_automatique',
            'nombre_questions_banque', 'points_total_banque', 'questions',
        ]

    def get_questions(self, obj):
        return QuestionAdminSerializer(obj.questions.all(), many=True).data


# =============================================================================
# Modules
# =============================================================================

class ModuleListeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    image_couverture = serializers.FileField(read_only=True, use_url=True)
    est_lu = serializers.SerializerMethodField()
    est_termine = serializers.SerializerMethodField()
    est_accessible = serializers.BooleanField(read_only=True)
    progression = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id', 'titre', 'slug', 'resume', 'niveau', 'ordre',
            'image_couverture', 'date_debut', 'date_fin', 'est_accessible',
            'est_lu', 'est_termine', 'progression',
        ]

    def _progression(self, obj):
        utilisateur = self.context.get('utilisateur')
        if utilisateur is None:
            return None
        return obj.progressions.filter(utilisateur_id=utilisateur.id).first()

    def get_est_lu(self, obj):
        progression = self._progression(obj)
        return bool(progression and progression.est_lu)

    def get_est_termine(self, obj):
        progression = self._progression(obj)
        return bool(progression and progression.est_termine)

    def get_progression(self, obj):
        progression = self._progression(obj)
        if progression is None:
            return {'pourcentage': 0, 'lecture': 0, 'quiz': 0, 'challenges': 0, 'challenges_termines': 0}
        nb = progression.challenges_termines
        return {
            'pourcentage': progression.pourcentage,
            'lecture': 25 if progression.est_lu else 0,
            'quiz': 25 if progression.quiz_reussi else 0,
            'challenges': min(nb, 2) * 25,
            'challenges_termines': nb,
        }


class ModuleDetailSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    image_couverture = serializers.FileField(read_only=True, use_url=True)
    video = serializers.FileField(read_only=True, use_url=True)
    illustrations = serializers.SerializerMethodField()
    ressources = serializers.SerializerMethodField()
    est_lu = serializers.SerializerMethodField()
    lu_le = serializers.SerializerMethodField()
    est_termine = serializers.SerializerMethodField()
    quiz_disponible = serializers.SerializerMethodField()
    est_accessible = serializers.BooleanField(read_only=True)
    progression = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id', 'titre', 'slug', 'contenu', 'resume', 'niveau', 'ordre',
            'video', 'image_couverture', 'illustrations', 'ressources',
            'date_debut', 'date_fin', 'est_accessible',
            'est_lu', 'lu_le', 'est_termine', 'quiz_disponible', 'progression',
        ]

    def _progression(self):
        return self.context.get('progression')

    def get_illustrations(self, obj):
        return IllustrationModuleSerializer(
            obj.illustrations.all(),
            many=True,
            context={'request': self.context.get('request')},
        ).data

    def get_ressources(self, obj):
        return RessourceModuleSerializer(
            obj.ressources.all(),
            many=True,
            context={'request': self.context.get('request')},
        ).data

    def get_est_lu(self, obj):
        progression = self._progression()
        return bool(progression and progression.est_lu)

    def get_lu_le(self, obj):
        progression = self._progression()
        return progression.lu_le if progression else None

    def get_est_termine(self, obj):
        progression = self._progression()
        return bool(progression and progression.est_termine)

    def get_quiz_disponible(self, obj):
        progression = self._progression()
        return bool(progression and progression.est_lu and hasattr(obj, 'quiz'))

    def get_progression(self, obj):
        progression = self._progression()
        if progression is None:
            return {'pourcentage': 0, 'lecture': 0, 'quiz': 0, 'challenges': 0, 'challenges_termines': 0}
        nb = progression.challenges_termines
        return {'pourcentage': progression.pourcentage, 'lecture': 25 if progression.est_lu else 0, 'quiz': 25 if progression.quiz_reussi else 0, 'challenges': min(nb, 2) * 25, 'challenges_termines': nb}


class ModuleAdminSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    image_couverture = serializers.FileField(read_only=True, use_url=True)
    video = serializers.FileField(read_only=True, use_url=True)
    illustrations = serializers.SerializerMethodField()
    ressources = serializers.SerializerMethodField()
    a_un_quiz = serializers.SerializerMethodField()
    nb_participants = serializers.SerializerMethodField()
    est_accessible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'titre', 'slug', 'contenu', 'resume', 'niveau', 'ordre',
            'est_publie', 'est_ouvert', 'date_debut', 'date_fin', 'est_accessible',
            'video', 'image_couverture', 'illustrations', 'ressources',
            'a_un_quiz', 'nb_participants', 'cree_le', 'modifie_le',
        ]

    def get_illustrations(self, obj):
        return IllustrationModuleSerializer(
            obj.illustrations.all(),
            many=True,
            context={'request': self.context.get('request')},
        ).data

    def get_ressources(self, obj):
        return RessourceModuleSerializer(
            obj.ressources.all(),
            many=True,
            context={'request': self.context.get('request')},
        ).data

    def get_a_un_quiz(self, obj):
        return hasattr(obj, 'quiz')

    def get_nb_participants(self, obj):
        return obj.progressions.count()


# =============================================================================
# Progression, tentatives et résultats
# =============================================================================

class ParticipantModuleSerializer(serializers.ModelSerializer):
    utilisateur_id = serializers.IntegerField(source='utilisateur.id', read_only=True)
    utilisateur_nom = serializers.SerializerMethodField()
    utilisateur_email = serializers.EmailField(source='utilisateur.email', read_only=True)

    class Meta:
        model = ProgressionModule
        fields = [
            'utilisateur_id', 'utilisateur_nom', 'utilisateur_email',
            'est_lu', 'lu_le', 'est_termine', 'termine_le',
        ]

    def get_utilisateur_nom(self, obj):
        return getattr(obj.utilisateur, 'full_name', None) or str(obj.utilisateur)


class ReponseQuizSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    question_id = serializers.UUIDField(source='question.uuid', read_only=True)
    question_texte = serializers.CharField(source='question.texte', read_only=True)
    type_question = serializers.CharField(source='question.type_question', read_only=True)
    choix_selectionnes = serializers.SerializerMethodField()

    class Meta:
        model = ReponseQuiz
        fields = [
            'id', 'question_id', 'question_texte', 'type_question',
            'choix_selectionnes', 'reponse_texte', 'est_correcte',
            'points_obtenus', 'enregistree_le', 'modifiee_le',
        ]

    def get_choix_selectionnes(self, obj):
        return [
            {'id': choix.uuid, 'texte': choix.texte}
            for choix in obj.choix_selectionnes.all()
        ]


class TentativeQuizSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    quiz_id = serializers.UUIDField(source='quiz.uuid', read_only=True)
    module_id = serializers.UUIDField(source='quiz.module.uuid', read_only=True)
    reponses = serializers.SerializerMethodField()
    nombre_questions = serializers.SerializerMethodField()
    nombre_reponses = serializers.SerializerMethodField()

    class Meta:
        model = TentativeQuiz
        fields = [
            'id', 'quiz_id', 'module_id', 'statut', 'score',
            'points_obtenus', 'points_total', 'est_reussi',
            'nombre_questions', 'nombre_reponses', 'cree_le', 'soumise_le', 'reponses',
        ]

    def get_nombre_questions(self, obj):
        return obj.questions_selectionnees.count()

    def get_nombre_reponses(self, obj):
        return obj.reponses.count()

    def get_reponses(self, obj):
        if obj.statut != TentativeQuiz.Statut.SOUMISE:
            return []
        return ReponseQuizSerializer(
            obj.reponses.select_related('question').prefetch_related('choix_selectionnes'),
            many=True,
        ).data


class ClassementEntreeSerializer(serializers.Serializer):
    rang = serializers.IntegerField()
    utilisateur_id = serializers.IntegerField()
    utilisateur_nom = serializers.CharField()
    meilleur_score = serializers.IntegerField()
    meilleurs_points = serializers.IntegerField()
    est_reussi = serializers.BooleanField()
    tentatives_effectuees = serializers.IntegerField()
    terminee_le = serializers.DateTimeField(allow_null=True)