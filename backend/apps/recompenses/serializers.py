from rest_framework import serializers
from .models import BadgeUtilisateur,Certificat,ConfigurationNiveau
class BadgeUtilisateurSerializer(serializers.ModelSerializer):
    nom=serializers.CharField(source='badge.nom',read_only=True)
    module=serializers.CharField(source='module.titre',read_only=True)
    class Meta: model=BadgeUtilisateur; fields=['id','nom','module','obtenu_le']
class CertificatSerializer(serializers.ModelSerializer):
    class Meta: model=Certificat; fields=['id','titre','niveau','fichier','delivre_le']
class ConfigurationNiveauSerializer(serializers.ModelSerializer):
    class Meta: model=ConfigurationNiveau; fields=['modules_pour_apprenti','modules_pour_actif','modules_pour_leader','modifie_le']
