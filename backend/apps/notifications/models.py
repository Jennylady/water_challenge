from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Notification personnelle envoyée à un utilisateur suite à un évènement de la plateforme."""

    class Type(models.TextChoices):
        NOUVEAU_MODULE = 'nouveau_module', 'Nouveau module disponible'
        QUIZ_DEBLOQUE = 'quiz_debloque', 'Quiz débloqué'
        DEFI_DEBLOQUE = 'defi_debloque', 'Défi débloqué'
        SOUMISSION_VALIDEE = 'soumission_validee', 'Soumission validée'
        SOUMISSION_REFUSEE = 'soumission_refusee', 'Soumission refusée'
        BADGE_OBTENU = 'badge_obtenu', 'Badge obtenu'
        CERTIFICAT_DELIVRE = 'certificat_delivre', 'Certificat délivré'
        NOUVEAU_COMMENTAIRE = 'nouveau_commentaire', 'Nouveau commentaire'
        NOUVELLE_MENTION_JAIME = 'nouvelle_mention_jaime', "Nouvelle mention j'aime"
        NIVEAU_ATTEINT = 'niveau_atteint', 'Nouveau niveau atteint'
        AUTRE = 'autre', 'Autre'

    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    type = models.CharField(max_length=30, choices=Type.choices, default=Type.AUTRE)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Lien interne vers la ressource concernée (ex: /defis/12/)",
    )
    est_lue = models.BooleanField(default=False)
    lue_le = models.DateTimeField(blank=True, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-cree_le']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f'{self.destinataire} - {self.titre}'


class Annonce(models.Model):
    """Annonce globale diffusée par un administrateur à tous les ambassadeurs (ou un public ciblé)."""

    class Portee(models.TextChoices):
        TOUS = 'tous', 'Tous les ambassadeurs'
        REGION = 'region', 'Une région spécifique'
        NIVEAU = 'niveau', 'Un niveau spécifique'

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='annonces_creees'
    )
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    portee = models.CharField(max_length=20, choices=Portee.choices, default=Portee.TOUS)
    region_ciblee = models.CharField(max_length=150, blank=True, null=True)
    niveau_cible = models.CharField(max_length=30, blank=True, null=True)
    est_active = models.BooleanField(default=True)
    publiee_le = models.DateTimeField(auto_now_add=True)
    expire_le = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'notifications_annonce'
        ordering = ['-publiee_le']
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'

    def __str__(self):
        return self.titre


class LectureAnnonce(models.Model):
    """Trace la lecture/le vu d'une annonce par un utilisateur (pour ne plus la ré-afficher)."""

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='annonces_lues'
    )
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='lectures')
    lue_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_lecture_annonce'
        unique_together = ('utilisateur', 'annonce')
        verbose_name = "Lecture d'annonce"
        verbose_name_plural = "Lectures d'annonce"

    def __str__(self):
        return f'{self.utilisateur} - {self.annonce.titre}'