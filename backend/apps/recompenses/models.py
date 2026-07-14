from django.db import models


class ConfigurationNiveau(models.Model):
    modules_pour_apprenti = models.PositiveIntegerField(default=2)
    modules_pour_actif = models.PositiveIntegerField(default=5)
    modules_pour_leader = models.PositiveIntegerField(default=8)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='recompenses_configuration_niveau'
        verbose_name='Configuration des niveaux'

    def save(self,*args,**kwargs):
        self.pk=1
        super().save(*args,**kwargs)

    @classmethod
    def charger(cls):
        obj,_=cls.objects.get_or_create(pk=1)
        return obj


class Badge(models.Model):
    nom=models.CharField(max_length=150, unique=True)
    description=models.TextField()
    icone=models.ImageField(upload_to='recompenses/badges/', blank=True, null=True)
    cree_le=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='recompenses_badge'
    def __str__(self): return self.nom


class BadgeUtilisateur(models.Model):
    utilisateur=models.ForeignKey('accounts_user.User',on_delete=models.CASCADE,related_name='badges')
    badge=models.ForeignKey(Badge,on_delete=models.CASCADE,related_name='attributions')
    module=models.ForeignKey('formation.Module',on_delete=models.CASCADE,related_name='badges_attribues')
    obtenu_le=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='recompenses_badge_utilisateur'
        constraints=[models.UniqueConstraint(fields=['utilisateur','module'],name='unique_badge_par_module_utilisateur')]


class Certificat(models.Model):
    utilisateur=models.ForeignKey('accounts_user.User',on_delete=models.CASCADE,related_name='certificats')
    titre=models.CharField(max_length=200)
    niveau=models.CharField(max_length=30)
    fichier=models.FileField(upload_to='recompenses/certificats/',blank=True,null=True)
    delivre_le=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='recompenses_certificat'
        constraints=[models.UniqueConstraint(fields=['utilisateur','niveau'],name='unique_certificat_niveau_utilisateur')]
