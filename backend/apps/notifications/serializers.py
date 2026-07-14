from rest_framework import serializers
from .models import Notification, Annonce

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id','type','titre','message','lien','est_lue','lue_le','cree_le']
        read_only_fields = fields

class AnnonceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annonce
        fields = ['id','titre','contenu','portee','region_ciblee','niveau_cible','publiee_le','expire_le']
        read_only_fields = fields
