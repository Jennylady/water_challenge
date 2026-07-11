from django.conf import settings
from rest_framework import serializers

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


def build_file_url(request, file_field):
    """Construit l'URL absolue réelle d'un fichier/image. Retourne None si le champ est vide."""
    if not file_field:
        return None
    try:
        relative_url = file_field.url
    except ValueError:
        return None
    if request is not None:
        return request.build_absolute_uri(relative_url)
    base_url = getattr(settings, 'BASE_URL', '')
    return f'{base_url}{relative_url}'


# ---------------------------------------------------------------------------
# Illustrations
# ---------------------------------------------------------------------------

class IllustrationModuleSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = IllustrationModule
        fields = ['id', 'legende', 'ordre', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        return build_file_url(request, obj.image)


# ---------------------------------------------------------------------------
# Choix - vue AMBASSADEUR (sans la bonne réponse) / vue ADMIN (avec correction)
# ---------------------------------------------------------------------------

class ChoixAmbassadeurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choix
        fields = ['id', 'texte']


class ChoixAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choix
        fields = ['id', 'texte', 'est_correct', 'explication']


# ---------------------------------------------------------------------------
# Question - vue AMBASSADEUR / ADMIN
# ---------------------------------------------------------------------------

class QuestionAmbassadeurSerializer(serializers.ModelSerializer):
    choix = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'texte', 'type_question', 'points', 'ordre', 'choix']

    def get_choix(self, obj):
        if obj.type_question == Question.TypeQuestion.REPONSE_COURTE:
            return []
        return ChoixAmbassadeurSerializer(obj.choix.all(), many=True).data


class QuestionAdminSerializer(serializers.ModelSerializer):
    choix = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'texte', 'type_question', 'points', 'ordre',
            'choix', 'reponses_acceptees', 'sensible_a_la_casse',
        ]

    def get_choix(self, obj):
        return ChoixAdminSerializer(obj.choix.all(), many=True).data


# ---------------------------------------------------------------------------
# Quiz - vue AMBASSADEUR / ADMIN
# ---------------------------------------------------------------------------

class QuizAmbassadeurSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'titre', 'score_de_reussite', 'questions']

    def get_questions(self, obj):
        return QuestionAmbassadeurSerializer(obj.questions.all(), many=True).data


class QuizAdminSerializer(serializers.ModelSerializer):
    module_id = serializers.IntegerField(source='module.id', read_only=True)
    points_total = serializers.IntegerField(read_only=True)
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'module_id', 'titre', 'score_de_reussite', 'points_total', 'questions']

    def get_questions(self, obj):
        return QuestionAdminSerializer(obj.questions.all(), many=True).data


# ---------------------------------------------------------------------------
# Module - vue AMBASSADEUR
# ---------------------------------------------------------------------------

class ModuleListeSerializer(serializers.ModelSerializer):
    """Liste des modules, avec la progression de l'utilisateur courant."""
    image_couverture_url = serializers.SerializerMethodField()
    est_lu = serializers.SerializerMethodField()
    est_termine = serializers.SerializerMethodField()
    est_accessible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'titre', 'slug', 'resume', 'niveau', 'ordre',
            'image_couverture_url', 'date_debut', 'date_fin', 'est_accessible',
            'est_lu', 'est_termine',
        ]

    def _get_progression(self, obj):
        utilisateur = self.context.get('utilisateur')
        if utilisateur is None:
            return None
        return obj.progressions.filter(utilisateur_id=utilisateur.id).first()

    def get_image_couverture_url(self, obj):
        request = self.context.get('request')
        return build_file_url(request, obj.image_couverture)

    def get_est_lu(self, obj):
        progression = self._get_progression(obj)
        return bool(progression and progression.est_lu)

    def get_est_termine(self, obj):
        progression = self._get_progression(obj)
        return bool(progression and progression.est_termine)


class ModuleDetailSerializer(serializers.ModelSerializer):
    """Détail d'un module (lecture) ; débloque automatiquement le quiz."""
    image_couverture_url = serializers.SerializerMethodField()
    illustrations = serializers.SerializerMethodField()
    est_lu = serializers.SerializerMethodField()
    lu_le = serializers.SerializerMethodField()
    est_termine = serializers.SerializerMethodField()
    quiz_disponible = serializers.SerializerMethodField()
    est_accessible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'titre', 'slug', 'contenu', 'resume', 'niveau', 'ordre',
            'url_video', 'image_couverture_url', 'illustrations',
            'date_debut', 'date_fin', 'est_accessible',
            'est_lu', 'lu_le', 'est_termine', 'quiz_disponible',
        ]

    def _get_progression(self, obj):
        return self.context.get('progression')

    def get_image_couverture_url(self, obj):
        request = self.context.get('request')
        return build_file_url(request, obj.image_couverture)

    def get_illustrations(self, obj):
        request = self.context.get('request')
        return IllustrationModuleSerializer(
            obj.illustrations.all(), many=True, context={'request': request}
        ).data

    def get_est_lu(self, obj):
        progression = self._get_progression(obj)
        return bool(progression and progression.est_lu)

    def get_lu_le(self, obj):
        progression = self._get_progression(obj)
        return progression.lu_le if progression else None

    def get_est_termine(self, obj):
        progression = self._get_progression(obj)
        return bool(progression and progression.est_termine)

    def get_quiz_disponible(self, obj):
        progression = self._get_progression(obj)
        a_lu = bool(progression and progression.est_lu)
        a_un_quiz = hasattr(obj, 'quiz') and obj.quiz is not None
        return a_lu and a_un_quiz


# ---------------------------------------------------------------------------
# Module - vue ADMIN
# ---------------------------------------------------------------------------

class ModuleAdminSerializer(serializers.ModelSerializer):
    image_couverture_url = serializers.SerializerMethodField()
    illustrations = serializers.SerializerMethodField()
    a_un_quiz = serializers.SerializerMethodField()
    nb_participants = serializers.SerializerMethodField()
    est_accessible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'titre', 'slug', 'contenu', 'resume', 'niveau', 'ordre',
            'est_publie', 'est_ouvert', 'date_debut', 'date_fin', 'est_accessible',
            'url_video', 'image_couverture_url', 'illustrations',
            'a_un_quiz', 'nb_participants', 'cree_le', 'modifie_le',
        ]

    def get_image_couverture_url(self, obj):
        request = self.context.get('request')
        return build_file_url(request, obj.image_couverture)

    def get_illustrations(self, obj):
        request = self.context.get('request')
        return IllustrationModuleSerializer(
            obj.illustrations.all(), many=True, context={'request': request}
        ).data

    def get_a_un_quiz(self, obj):
        return hasattr(obj, 'quiz') and obj.quiz is not None

    def get_nb_participants(self, obj):
        return obj.progressions.count()


# ---------------------------------------------------------------------------
# Participants d'un module (admin)
# ---------------------------------------------------------------------------

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
        return getattr(obj.utilisateur, 'full_name', str(obj.utilisateur))


# ---------------------------------------------------------------------------
# Tentatives de quiz
# ---------------------------------------------------------------------------

class ReponseQuizSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source='question.id', read_only=True)
    question_texte = serializers.CharField(source='question.texte', read_only=True)
    type_question = serializers.CharField(source='question.type_question', read_only=True)
    choix_selectionnes = serializers.SerializerMethodField()

    class Meta:
        model = ReponseQuiz
        fields = [
            'id', 'question_id', 'question_texte', 'type_question',
            'choix_selectionnes', 'reponse_texte', 'est_correcte', 'points_obtenus',
        ]

    def get_choix_selectionnes(self, obj):
        return [{'id': c.id, 'texte': c.texte} for c in obj.choix_selectionnes.all()]


class TentativeQuizSerializer(serializers.ModelSerializer):
    quiz_id = serializers.IntegerField(source='quiz.id', read_only=True)
    module_id = serializers.IntegerField(source='quiz.module.id', read_only=True)
    reponses = serializers.SerializerMethodField()

    class Meta:
        model = TentativeQuiz
        fields = [
            'id', 'quiz_id', 'module_id', 'score', 'points_obtenus', 'points_total',
            'est_reussi', 'cree_le', 'reponses',
        ]

    def get_reponses(self, obj):
        return ReponseQuizSerializer(obj.reponses.all(), many=True).data


# ---------------------------------------------------------------------------
# Classement (leaderboard) d'un module
# ---------------------------------------------------------------------------

class ClassementEntreeSerializer(serializers.Serializer):
    """
    Entrée agrégée de classement (pas liée à une seule instance de modèle,
    construite à partir d'une agrégation de TentativeQuiz).
    """
    rang = serializers.IntegerField()
    utilisateur_id = serializers.IntegerField()
    utilisateur_nom = serializers.CharField()
    meilleur_score = serializers.IntegerField()
    meilleurs_points = serializers.IntegerField()
    est_reussi = serializers.BooleanField()
    tentatives_effectuees = serializers.IntegerField()
    terminee_le = serializers.DateTimeField(allow_null=True)