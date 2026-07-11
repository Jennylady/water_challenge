from django.db import models
from django.conf import settings


class Badge(models.Model):
    """Badge débloqué selon les réalisations (points ou nombre de défis complétés)."""

    nom = models.CharField(max_length=150)
    description = models.TextField()
    icone = models.ImageField(upload_to='recompenses/badges/')
    points_requis = models.PositiveIntegerField(blank=True, null=True)
    defis_requis = models.PositiveIntegerField(
        blank=True, null=True, help_text="Nombre de défis validés requis"
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recompenses_badge'
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'

    def __str__(self):
        return self.nom


class BadgeUtilisateur(models.Model):
    """Badge effectivement obtenu par un utilisateur."""

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges'
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='badges_utilisateur')
    obtenu_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recompenses_badge_utilisateur'
        unique_together = ('utilisateur', 'badge')
        ordering = ['-obtenu_le']
        verbose_name = 'Badge utilisateur'
        verbose_name_plural = 'Badges utilisateur'

    def __str__(self):
        return f'{self.utilisateur} - {self.badge.nom}'


class Certificat(models.Model):
    """Certificat officiel délivré à un utilisateur, téléchargeable depuis son profil."""

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificats'
    )
    titre = models.CharField(max_length=200)
    niveau = models.CharField(max_length=30)
    fichier = models.FileField(upload_to='recompenses/certificats/')
    delivre_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recompenses_certificat'
        ordering = ['-delivre_le']
        verbose_name = 'Certificat'
        verbose_name_plural = 'Certificats'

    def __str__(self):
        return f'{self.utilisateur} - {self.titre}'