from django.db import models
from django.conf import settings
from django.utils import timezone


class Module(models.Model):
    """Un module de formation courte (lecture de 2 à 5 minutes)."""

    class Niveau(models.TextChoices):
        DEBUTANT = 'débutant', 'Débutant'
        APPRENTI = 'apprenti', 'Apprenti Ambassadeur'
        ACTIF = 'actif', 'Ambassadeur actif'
        LEADER = 'leader', 'Leader communautaire'

    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    contenu = models.TextField(help_text="Contenu de lecture (2 à 5 minutes)")
    resume = models.TextField(help_text="Résumé des points essentiels")
    image_couverture = models.ImageField(
        upload_to='formation/modules/couvertures/', blank=True, null=True
    )
    url_video = models.URLField(blank=True, null=True, help_text="Vidéo facultative")
    niveau = models.CharField(max_length=30, choices=Niveau.choices, default=Niveau.DEBUTANT)
    ordre = models.PositiveIntegerField(default=0)
    est_publie = models.BooleanField(default=True)

    # --- Ouverture / fermeture de la formation (module) ---
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
        """Un module est accessible s'il est publié, ouvert manuellement, et dans sa fenêtre de dates."""
        if not self.est_publie or not self.est_ouvert:
            return False
        maintenant = timezone.now()
        if self.date_debut and maintenant < self.date_debut:
            return False
        if self.date_fin and maintenant > self.date_fin:
            return False
        return True


class IllustrationModule(models.Model):
    """Illustrations et infographies rattachées à un module."""

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='illustrations')
    image = models.ImageField(upload_to='formation/modules/illustrations/')
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
    """Suivi de la lecture et de la complétion d'un module par un utilisateur (= participation)."""

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
        unique_together = ('utilisateur', 'module')
        verbose_name = 'Progression de module'
        verbose_name_plural = 'Progressions de module'

    def __str__(self):
        return f'{self.utilisateur} - {self.module.titre}'


class Quiz(models.Model):
    """Quiz de validation des connaissances, débloqué après lecture du module."""

    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='quiz')
    titre = models.CharField(max_length=200)
    score_de_reussite = models.PositiveIntegerField(
        default=50, help_text="Score minimum en % pour valider le quiz"
    )

    class Meta:
        db_table = 'formation_quiz'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'

    def __str__(self):
        return f'Quiz - {self.module.titre}'

    @property
    def points_total(self):
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    """Une question de quiz : à choix unique, à choix multiple, ou à réponse courte."""

    class TypeQuestion(models.TextChoices):
        CHOIX_UNIQUE = 'choix_unique', 'Choix unique'
        CHOIX_MULTIPLE = 'choix_multiple', 'Choix multiple'
        REPONSE_COURTE = 'reponse_courte', 'Réponse courte'

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    texte = models.CharField(max_length=500)
    type_question = models.CharField(
        max_length=30, choices=TypeQuestion.choices, default=TypeQuestion.CHOIX_UNIQUE
    )
    points = models.PositiveIntegerField(default=1, help_text="Points attribués si la question est correcte")
    ordre = models.PositiveIntegerField(default=0)

    # Utilisé uniquement si type_question == REPONSE_COURTE
    reponses_acceptees = models.JSONField(
        default=list, blank=True,
        help_text="Liste des réponses valides (texte libre) pour une question de type 'réponse courte'",
    )
    sensible_a_la_casse = models.BooleanField(
        default=False, help_text="Si True, la casse est prise en compte pour une réponse courte"
    )

    class Meta:
        db_table = 'formation_question'
        ordering = ['ordre']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return self.texte


class Choix(models.Model):
    """Choix de réponse pour une question à choix unique ou multiple."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix')
    texte = models.CharField(max_length=255)
    est_correct = models.BooleanField(default=False)
    explication = models.TextField(
        blank=True, null=True, help_text="Explication affichée après correction (facultatif)"
    )

    class Meta:
        db_table = 'formation_choix'
        verbose_name = 'Choix'
        verbose_name_plural = 'Choix'

    def __str__(self):
        return self.texte


class TentativeQuiz(models.Model):
    """Une tentative de quiz par un utilisateur (recommençable pour améliorer le score)."""

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tentatives_quiz'
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='tentatives')
    score = models.PositiveIntegerField(default=0, help_text="Score obtenu en % (scoring automatique)")
    points_obtenus = models.PositiveIntegerField(default=0)
    points_total = models.PositiveIntegerField(default=0)
    est_reussi = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'formation_tentative_quiz'
        ordering = ['-cree_le']
        verbose_name = 'Tentative de quiz'
        verbose_name_plural = 'Tentatives de quiz'

    def __str__(self):
        return f'{self.utilisateur} - {self.quiz.titre} - {self.score}%'


class ReponseQuiz(models.Model):
    """
    Réponse donnée par l'utilisateur à une question, pour une tentative donnée.
    - choix_selectionnes : utilisé pour choix_unique / choix_multiple
    - reponse_texte : utilisé pour reponse_courte
    Correction et points calculés automatiquement (scoring automatique en fin de quiz).
    """

    tentative = models.ForeignKey(TentativeQuiz, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reponses')
    choix_selectionnes = models.ManyToManyField(Choix, blank=True, related_name='+')
    reponse_texte = models.CharField(max_length=500, blank=True, null=True)
    est_correcte = models.BooleanField(default=False)
    points_obtenus = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'formation_reponse_quiz'
        verbose_name = 'Réponse de quiz'
        verbose_name_plural = 'Réponses de quiz'

    def __str__(self):
        return f'{self.tentative} - {self.question}'