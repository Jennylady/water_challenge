from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Defi(models.Model):
    """Mission concrète réalisée par un ambassadeur après la validation d'un quiz."""

    class Niveau(models.TextChoices):
        DEBUTANT = 'debutant', 'Débutant'
        APPRENTI = 'apprenti', 'Apprenti Ambassadeur'
        ACTIF = 'actif', 'Ambassadeur actif'
        LEADER = 'leader', 'Leader communautaire'

    module = models.ForeignKey(
        'formation.Module',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='defis',
        help_text="Module dont le quiz débloque ce défi. Laisser vide pour un défi libre.",
    )
    titre = models.CharField(max_length=200)
    description = models.TextField(help_text="Description détaillée de la mission")
    resultat_attendu = models.TextField(help_text="Objectif attendu")
    criteres_validation = models.TextField(help_text="Critères utilisés par le validateur")
    image_couverture = models.ImageField(
        upload_to='challenges/defis/couvertures/', blank=True, null=True
    )
    niveau = models.CharField(max_length=30, choices=Niveau.choices, default=Niveau.DEBUTANT)
    ordre = models.PositiveIntegerField(default=0)
    duree_estimee = models.CharField(max_length=100, help_text="Ex. : 30 minutes, 1 semaine")
    points_recompense = models.PositiveIntegerField(default=10)

    nombre_photos_min = models.PositiveSmallIntegerField(default=1)
    nombre_photos_max = models.PositiveSmallIntegerField(default=5)
    video_obligatoire = models.BooleanField(default=False)
    est_obligatoire = models.BooleanField(
        default=True,
        help_text="Un défi obligatoire doit être validé pour débloquer le module suivant.",
    )

    est_actif = models.BooleanField(default=True)
    est_publie = models.BooleanField(default=True)
    est_ouvert = models.BooleanField(default=True)
    date_debut = models.DateTimeField(blank=True, null=True)
    date_fin = models.DateTimeField(blank=True, null=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'challenges_defi'
        ordering = ['niveau', 'ordre', '-cree_le']
        verbose_name = 'Défi'
        verbose_name_plural = 'Défis'
        constraints = [
            models.CheckConstraint(
                check=Q(points_recompense__gte=0),
                name='challenges_defi_points_non_negatifs',
            ),
            models.CheckConstraint(
                check=Q(nombre_photos_max__gte=F('nombre_photos_min')),
                name='challenges_defi_photos_max_gte_min',
            ),
        ]

    def __str__(self):
        return self.titre

    def clean(self):
        erreurs = {}
        if self.date_debut and self.date_fin and self.date_fin <= self.date_debut:
            erreurs['date_fin'] = "La date de fin doit être postérieure à la date de début."
        if self.nombre_photos_max < self.nombre_photos_min:
            erreurs['nombre_photos_max'] = (
                "Le nombre maximal de photos doit être supérieur ou égal au minimum."
            )
        if erreurs:
            raise ValidationError(erreurs)

    @property
    def est_accessible(self):
        if not self.est_actif or not self.est_publie or not self.est_ouvert:
            return False
        maintenant = timezone.now()
        if self.date_debut and maintenant < self.date_debut:
            return False
        if self.date_fin and maintenant > self.date_fin:
            return False
        return True


class DefiUtilisateur(models.Model):
    """État du défi pour un utilisateur : verrouillé, disponible, en cours ou terminé."""

    class Statut(models.TextChoices):
        VERROUILLE = 'verrouille', 'Verrouillé'
        DISPONIBLE = 'disponible', 'Disponible'
        EN_COURS = 'en_cours', 'En cours'
        TERMINE = 'termine', 'Terminé'

    utilisateur = models.ForeignKey(
        'accounts_user.User',
        on_delete=models.CASCADE,
        related_name='defis_utilisateur',
    )
    defi = models.ForeignKey(Defi, on_delete=models.CASCADE, related_name='defis_utilisateur')
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.VERROUILLE)
    debloque_le = models.DateTimeField(blank=True, null=True)
    commence_le = models.DateTimeField(blank=True, null=True)
    termine_le = models.DateTimeField(blank=True, null=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'challenges_defi_utilisateur'
        constraints = [
            models.UniqueConstraint(
                fields=['utilisateur', 'defi'],
                name='challenges_unique_defi_utilisateur',
            ),
        ]
        verbose_name = 'Défi utilisateur'
        verbose_name_plural = 'Défis utilisateur'

    def __str__(self):
        return f'{self.utilisateur} - {self.defi.titre} ({self.statut})'


class SoumissionActivite(models.Model):
    """Preuves envoyées par un ambassadeur pour un défi réalisé."""

    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        VALIDEE = 'validee', 'Validée'
        REFUSEE = 'refusee', 'Refusée'

    utilisateur = models.ForeignKey(
        'accounts_user.User',
        on_delete=models.CASCADE,
        related_name='soumissions_activite',
    )
    defi = models.ForeignKey(Defi, on_delete=models.CASCADE, related_name='soumissions')
    rapport = models.TextField(help_text="Court rapport rédigé par l'ambassadeur")
    date_activite = models.DateField()
    lieu = models.CharField(max_length=255)
    nombre_personnes_sensibilisees = models.PositiveIntegerField(default=0)
    video = models.FileField(upload_to='challenges/soumissions/videos/', blank=True, null=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    soumis_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    traitee_le = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'challenges_soumission_activite'
        ordering = ['-soumis_le']
        verbose_name = "Soumission d'activité"
        verbose_name_plural = "Soumissions d'activité"
        constraints = [
            models.UniqueConstraint(
                fields=['utilisateur', 'defi'],
                condition=Q(statut='en_attente'),
                name='challenges_unique_soumission_en_attente',
            ),
            models.CheckConstraint(
                check=Q(nombre_personnes_sensibilisees__gte=0),
                name='challenges_personnes_sensibilisees_non_negatif',
            ),
        ]

    def __str__(self):
        return f'{self.utilisateur} - {self.defi.titre} - {self.statut}'


class PhotoSoumission(models.Model):
    soumission = models.ForeignKey(
        SoumissionActivite, on_delete=models.CASCADE, related_name='photos'
    )
    image = models.ImageField(upload_to='challenges/soumissions/photos/')
    ordre = models.PositiveSmallIntegerField(default=0)
    ajoutee_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'challenges_photo_soumission'
        ordering = ['ordre', 'id']
        verbose_name = 'Photo de soumission'
        verbose_name_plural = 'Photos de soumission'

    def __str__(self):
        return f'Photo - {self.soumission}'


class Validation(models.Model):
    """Décision d'un validateur sur une soumission d'activité."""

    class Decision(models.TextChoices):
        ACCEPTEE = 'acceptee', 'Acceptée'
        REFUSEE = 'refusee', 'Refusée'

    soumission = models.OneToOneField(
        SoumissionActivite, on_delete=models.CASCADE, related_name='validation'
    )
    validateur = models.ForeignKey(
        'accounts_user.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='validations',
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    commentaire = models.TextField(blank=True, null=True)
    points_attribues = models.PositiveIntegerField(default=0)
    points_appliques = models.BooleanField(
        default=False,
        help_text="Garantit que les points ne sont ajoutés qu'une seule fois.",
    )
    valide_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'challenges_validation'
        verbose_name = 'Validation'
        verbose_name_plural = 'Validations'

    def __str__(self):
        return f'Validation - {self.soumission} - {self.decision}'