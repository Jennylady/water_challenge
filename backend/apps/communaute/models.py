from django.db import models
from django.conf import settings


class ProjetCommunautaire(models.Model):
    """Projet personnel créé par un ambassadeur, avec équipe et suivi d'impact."""

    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projets_crees'
    )
    titre = models.CharField(max_length=200)
    objectif = models.TextField()
    lieu = models.CharField(max_length=255)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    personnes_impactees = models.PositiveIntegerField(default=0)
    actions_realisees = models.PositiveIntegerField(default=0)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'communaute_projet'
        ordering = ['-cree_le']
        verbose_name = 'Projet communautaire'
        verbose_name_plural = 'Projets communautaires'

    def __str__(self):
        return self.titre


class MembreProjet(models.Model):
    """Membre de l'équipe rattaché à un projet communautaire."""

    projet = models.ForeignKey(ProjetCommunautaire, on_delete=models.CASCADE, related_name='membres')
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projets_rejoints'
    )
    rejoint_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'communaute_membre_projet'
        unique_together = ('projet', 'utilisateur')
        verbose_name = 'Membre de projet'
        verbose_name_plural = 'Membres de projet'

    def __str__(self):
        return f'{self.utilisateur} - {self.projet.titre}'


class PhotoProjet(models.Model):
    """Photo de l'avancement d'un projet communautaire."""

    projet = models.ForeignKey(ProjetCommunautaire, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='communaute/projets/photos/')
    legende = models.CharField(max_length=255, blank=True, null=True)
    publiee_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'communaute_photo_projet'
        ordering = ['-publiee_le']
        verbose_name = 'Photo de projet'
        verbose_name_plural = 'Photos de projet'

    def __str__(self):
        return f'Photo - {self.projet.titre}'


class Publication(models.Model):
    """Actualité, expérience partagée ou question posée par un ambassadeur."""

    class Type(models.TextChoices):
        ACTUALITE = 'actualite', 'Actualité'
        EXPERIENCE = 'experience', 'Expérience'
        QUESTION = 'question', 'Question'

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='publications'
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.ACTUALITE)
    contenu = models.TextField()
    image = models.ImageField(upload_to='communaute/publications/', blank=True, null=True)
    meilleure_reponse = models.ForeignKey(
        'Commentaire',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+',
        help_text="Réponse marquée comme la meilleure (pertinent pour les questions)",
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'communaute_publication'
        ordering = ['-cree_le']
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'

    def __str__(self):
        return f'{self.auteur} - {self.get_type_display()}'


class Commentaire(models.Model):
    """Commentaire (plat) sous une publication."""

    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name='commentaires'
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commentaires'
    )
    contenu = models.TextField()
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'communaute_commentaire'
        ordering = ['cree_le']
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'

    def __str__(self):
        return f'{self.auteur} - {self.publication}'


class MentionJaimePublication(models.Model):
    """J'aime sur une publication."""

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='publications_aimees'
    )
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name='mentions_jaime'
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'communaute_mention_jaime_publication'
        unique_together = ('utilisateur', 'publication')
        verbose_name = "J'aime (publication)"
        verbose_name_plural = "J'aime (publications)"

    def __str__(self):
        return f'{self.utilisateur} aime {self.publication}'


class MentionJaimeCommentaire(models.Model):
    """J'aime sur un commentaire."""

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commentaires_aimes'
    )
    commentaire = models.ForeignKey(
        Commentaire, on_delete=models.CASCADE, related_name='mentions_jaime'
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'communaute_mention_jaime_commentaire'
        unique_together = ('utilisateur', 'commentaire')
        verbose_name = "J'aime (commentaire)"
        verbose_name_plural = "J'aime (commentaires)"

    def __str__(self):
        return f'{self.utilisateur} aime {self.commentaire}'