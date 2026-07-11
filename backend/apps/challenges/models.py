from django.db import models
from django.conf import settings


class Defi(models.Model):
    """Une mission concrète à réaliser dans la communauté (ex: sensibiliser 5 personnes)."""

    class Niveau(models.TextChoices):
        DEBUTANT = 'debutant', 'Débutant'
        APPRENTI = 'apprenti', 'Apprenti Ambassadeur'
        ACTIF = 'actif', 'Ambassadeur actif'
        LEADER = 'leader', 'Leader communautaire'

    module = models.ForeignKey(
        'formation.Module', on_delete=models.SET_NULL, blank=True, null=True, related_name='defis'
    )
    titre = models.CharField(max_length=200)
    description = models.TextField(help_text="Description de la mission")
    resultat_attendu = models.TextField(help_text="Objectif attendu")
    criteres_validation = models.TextField(help_text="Critères de validation")
    niveau = models.CharField(max_length=30, choices=Niveau.choices, default=Niveau.DEBUTANT)
    duree_estimee = models.CharField(max_length=100, help_text="Ex: 30 minutes, 1 semaine")
    points_recompense = models.PositiveIntegerField(default=10)
    est_actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'challenges_defi'
        ordering = ['niveau', '-cree_le']
        verbose_name = 'Défi'
        verbose_name_plural = 'Défis'

    def __str__(self):
        return self.titre


class DefiUtilisateur(models.Model):
    """Suivi de l'état d'un défi pour un utilisateur (verrouillé, en cours, terminé)."""

    class Statut(models.TextChoices):
        VERROUILLE = 'verrouille', 'Verrouillé'
        DISPONIBLE = 'disponible', 'Disponible'
        EN_COURS = 'en_cours', 'En cours'
        TERMINE = 'termine', 'Terminé'

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='defis_utilisateur'
    )
    defi = models.ForeignKey(Defi, on_delete=models.CASCADE, related_name='defis_utilisateur')
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.VERROUILLE)
    debloque_le = models.DateTimeField(blank=True, null=True)
    termine_le = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'challenges_defi_utilisateur'
        unique_together = ('utilisateur', 'defi')
        verbose_name = 'Défi utilisateur'
        verbose_name_plural = 'Défis utilisateur'

    def __str__(self):
        return f'{self.utilisateur} - {self.defi.titre} ({self.statut})'


class SoumissionActivite(models.Model):
    """Preuves envoyées par l'ambassadeur pour un défi réalisé."""

    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        VALIDEE = 'validee', 'Validée'
        REFUSEE = 'refusee', 'Refusée'

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='soumissions_activite'
    )
    defi = models.ForeignKey(Defi, on_delete=models.CASCADE, related_name='soumissions')
    rapport = models.TextField(help_text="Court rapport rédigé par l'ambassadeur")
    date_activite = models.DateField()
    lieu = models.CharField(max_length=255)
    nombre_personnes_sensibilisees = models.PositiveIntegerField(default=0)
    video = models.FileField(
        upload_to='challenges/soumissions/videos/', blank=True, null=True
    )
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    soumis_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'challenges_soumission_activite'
        ordering = ['-soumis_le']
        verbose_name = "Soumission d'activité"
        verbose_name_plural = "Soumissions d'activité"

    def __str__(self):
        return f'{self.utilisateur} - {self.defi.titre} - {self.statut}'


class PhotoSoumission(models.Model):
    soumission = models.ForeignKey(
        SoumissionActivite, on_delete=models.CASCADE, related_name='photos'
    )
    image = models.ImageField(upload_to='challenges/soumissions/photos/')

    class Meta:
        db_table = 'challenges_photo_soumission'
        verbose_name = 'Photo de soumission'
        verbose_name_plural = 'Photos de soumission'

    def __str__(self):
        return f'Photo - {self.soumission}'


class Validation(models.Model):
    """Décision d'un administrateur ou mentor sur une soumission d'activité."""

    class Decision(models.TextChoices):
        ACCEPTEE = 'acceptee', 'Acceptée'
        REFUSEE = 'refusee', 'Refusée'

    soumission = models.OneToOneField(
        SoumissionActivite, on_delete=models.CASCADE, related_name='validation'
    )
    validateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='validations'
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    commentaire = models.TextField(blank=True, null=True)
    points_attribues = models.PositiveIntegerField(default=0)
    valide_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'challenges_validation'
        verbose_name = 'Validation'
        verbose_name_plural = 'Validations'

    def __str__(self):
        return f'Validation - {self.soumission} - {self.decision}'

