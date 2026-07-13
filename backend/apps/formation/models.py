import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Module(models.Model):
    """Un module de formation courte (lecture de 2 à 5 minutes)."""

    class Niveau(models.TextChoices):
        DEBUTANT = 'débutant', 'Débutant'
        APPRENTI = 'apprenti', 'Apprenti Ambassadeur'
        ACTIF = 'actif', 'Ambassadeur actif'
        LEADER = 'leader', 'Leader communautaire'

    # L'identifiant public exposé par l'API et utilisé dans les URL.
    # La clé primaire interne reste inchangée pour permettre une migration sûre
    # depuis la base existante et préserver toutes les relations inter-applications.
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    contenu = models.TextField(help_text="Contenu de lecture (2 à 5 minutes)")
    resume = models.TextField(help_text="Résumé des points essentiels")
    image_couverture = models.FileField(
        upload_to='formation/modules/couvertures/',
        blank=True,
        null=True,
        help_text="Image de couverture téléversée (facultative)",
    )
    video = models.FileField(
        upload_to='formation/modules/videos/',
        blank=True,
        null=True,
        help_text="Fichier vidéo téléversé (facultatif)",
    )
    niveau = models.CharField(max_length=30, choices=Niveau.choices, default=Niveau.DEBUTANT)
    ordre = models.PositiveIntegerField(default=0)
    est_publie = models.BooleanField(default=True)
    est_ouvert = models.BooleanField(
        default=True,
        help_text=(
            "Ouverture/fermeture manuelle. Prioritaire sur la fenêtre de dates : "
            "si False, le module est fermé même si date_debut/date_fin l'autoriseraient."
        ),
    )
    date_debut = models.DateTimeField(
        blank=True, null=True, help_text="Date/heure d'ouverture programmée (facultatif)"
    )
    date_fin = models.DateTimeField(
        blank=True, null=True, help_text="Date/heure de fermeture programmée (facultatif)"
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'formation_module'
        ordering = ['niveau', 'ordre']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'

    def __str__(self):
        return self.titre

    @property
    def est_accessible(self):
        if not self.est_publie or not self.est_ouvert:
            return False
        maintenant = timezone.now()
        if self.date_debut and maintenant < self.date_debut:
            return False
        if self.date_fin and maintenant > self.date_fin:
            return False
        return True


class IllustrationModule(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='illustrations')
    image = models.FileField(
        upload_to='formation/modules/illustrations/',
        help_text="Fichier d'illustration téléversé",
    )
    legende = models.CharField(max_length=255, blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'formation_illustration_module'
        ordering = ['ordre']
        verbose_name = 'Illustration de module'
        verbose_name_plural = 'Illustrations de module'

    def __str__(self):
        return f'{self.module.titre} - illustration {self.ordre}'


class ProgressionModule(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progressions_module'
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progressions')
    est_lu = models.BooleanField(default=False)
    lu_le = models.DateTimeField(blank=True, null=True)
    est_termine = models.BooleanField(
        default=False, help_text="Terminé = module lu ET quiz réussi"
    )
    termine_le = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'formation_progression_module'
        constraints = [
            models.UniqueConstraint(
                fields=['utilisateur', 'module'], name='unique_progression_utilisateur_module'
            ),
        ]
        verbose_name = 'Progression de module'
        verbose_name_plural = 'Progressions de module'

    def __str__(self):
        return f'{self.utilisateur} - {self.module.titre}'


class Quiz(models.Model):
    """Un module possède au maximum un quiz et chaque quiz possède une banque de questions."""

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='quiz')
    titre = models.CharField(max_length=200)
    score_de_reussite = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score minimum en % pour valider le quiz",
    )
    nombre_questions = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        help_text="Nombre de questions tirées aléatoirement dans la banque pour une tentative",
    )
    correction_automatique = models.BooleanField(
        default=True,
        help_text=(
            "Si activée, l'API indique immédiatement si une réponse est correcte et, "
            "en cas d'erreur, retourne la correction et l'explication disponible."
        ),
    )

    class Meta:
        db_table = 'formation_quiz'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'

    def __str__(self):
        return f'Quiz - {self.module.titre}'

    @property
    def points_total_banque(self):
        return sum(q.points for q in self.questions.all())

    @property
    def nombre_questions_banque(self):
        return self.questions.count()


class Question(models.Model):
    class TypeQuestion(models.TextChoices):
        CHOIX_UNIQUE = 'choix_unique', 'Choix unique'
        CHOIX_MULTIPLE = 'choix_multiple', 'Choix multiple'
        REPONSE_COURTE = 'reponse_courte', 'Réponse courte'

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    texte = models.CharField(max_length=500)
    type_question = models.CharField(
        max_length=30, choices=TypeQuestion.choices, default=TypeQuestion.CHOIX_UNIQUE
    )
    points = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)],
        help_text="Points attribués si la question est correcte",
    )
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre dans la banque de questions")
    explication = models.TextField(
        blank=True, null=True,
        help_text="Explication générale retournée lors d'une correction automatique",
    )
    reponses_acceptees = models.JSONField(
        default=list, blank=True,
        help_text="Réponses valides pour une question de type réponse_courte",
    )
    sensible_a_la_casse = models.BooleanField(default=False)

    class Meta:
        db_table = 'formation_question'
        ordering = ['ordre', 'id']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return self.texte


class Choix(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix')
    texte = models.CharField(max_length=255)
    est_correct = models.BooleanField(default=False)
    explication = models.TextField(
        blank=True, null=True, help_text="Explication affichée après correction (facultatif)"
    )

    class Meta:
        db_table = 'formation_choix'
        ordering = ['id']
        verbose_name = 'Choix'
        verbose_name_plural = 'Choix'

    def __str__(self):
        return self.texte


class TentativeQuiz(models.Model):
    class Statut(models.TextChoices):
        EN_COURS = 'en_cours', 'En cours'
        SOUMISE = 'soumise', 'Soumise'

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tentatives_quiz'
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='tentatives')
    questions_tirees = models.ManyToManyField(
        Question,
        through='QuestionTentative',
        related_name='tentatives_tirees',
    )
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_COURS)
    score = models.PositiveIntegerField(
        default=0, help_text="Score obtenu en % (scoring automatique)"
    )
    points_obtenus = models.PositiveIntegerField(default=0)
    points_total = models.PositiveIntegerField(default=0)
    est_reussi = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)
    soumise_le = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'formation_tentative_quiz'
        ordering = ['-cree_le']
        constraints = [
            models.UniqueConstraint(
                fields=['utilisateur', 'quiz'],
                condition=Q(statut='en_cours'),
                name='unique_tentative_quiz_en_cours',
            ),
        ]
        verbose_name = 'Tentative de quiz'
        verbose_name_plural = 'Tentatives de quiz'

    def __str__(self):
        return f'{self.utilisateur} - {self.quiz.titre} - {self.statut}'


class QuestionTentative(models.Model):
    """Fige les questions et leur ordre aléatoire pour une tentative précise."""

    tentative = models.ForeignKey(
        TentativeQuiz, on_delete=models.CASCADE, related_name='questions_selectionnees'
    )
    question = models.ForeignKey(
        Question, on_delete=models.RESTRICT, related_name='tirages'
    )
    ordre = models.PositiveIntegerField()

    class Meta:
        db_table = 'formation_question_tentative'
        ordering = ['ordre']
        constraints = [
            models.UniqueConstraint(
                fields=['tentative', 'question'], name='unique_question_par_tentative'
            ),
            models.UniqueConstraint(
                fields=['tentative', 'ordre'], name='unique_ordre_par_tentative'
            ),
        ]
        verbose_name = 'Question tirée'
        verbose_name_plural = 'Questions tirées'

    def __str__(self):
        return f'{self.tentative} - Q{self.ordre}'


class ReponseQuiz(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    tentative = models.ForeignKey(TentativeQuiz, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(Question, on_delete=models.RESTRICT, related_name='reponses')
    choix_selectionnes = models.ManyToManyField(Choix, blank=True, related_name='+')
    reponse_texte = models.CharField(max_length=500, blank=True, null=True)
    est_correcte = models.BooleanField(default=False)
    points_obtenus = models.PositiveIntegerField(default=0)
    enregistree_le = models.DateTimeField(auto_now_add=True)
    modifiee_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'formation_reponse_quiz'
        constraints = [
            models.UniqueConstraint(
                fields=['tentative', 'question'], name='unique_reponse_question_tentative'
            ),
        ]
        verbose_name = 'Réponse de quiz'
        verbose_name_plural = 'Réponses de quiz'

    def __str__(self):
        return f'{self.tentative} - {self.question}'