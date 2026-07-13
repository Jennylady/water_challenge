from django.conf import settings
from rest_framework import serializers

from .models import Defi, DefiUtilisateur, PhotoSoumission, SoumissionActivite, Validation


def build_file_url(request, file_field):
    if not file_field:
        return None
    try:
        relative_url = file_field.url
    except ValueError:
        return None
    if request is not None:
        return request.build_absolute_uri(relative_url)
    return f"{getattr(settings, 'BASE_URL', '')}{relative_url}"


def nom_utilisateur(utilisateur):
    return getattr(utilisateur, 'full_name', None) or str(utilisateur)


class PhotoSoumissionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PhotoSoumission
        fields = ['id', 'ordre', 'image_url', 'ajoutee_le']

    def get_image_url(self, obj):
        return build_file_url(self.context.get('request'), obj.image)


class ValidationSerializer(serializers.ModelSerializer):
    validateur_id = serializers.IntegerField(source='validateur.id', read_only=True, allow_null=True)
    validateur_nom = serializers.SerializerMethodField()

    class Meta:
        model = Validation
        fields = [
            'id', 'decision', 'commentaire', 'points_attribues',
            'validateur_id', 'validateur_nom', 'valide_le',
        ]

    def get_validateur_nom(self, obj):
        return nom_utilisateur(obj.validateur) if obj.validateur else None


class SoumissionActiviteSerializer(serializers.ModelSerializer):
    defi_id = serializers.IntegerField(source='defi.id', read_only=True)
    defi_titre = serializers.CharField(source='defi.titre', read_only=True)
    utilisateur_id = serializers.IntegerField(source='utilisateur.id', read_only=True)
    utilisateur_nom = serializers.SerializerMethodField()
    utilisateur_email = serializers.EmailField(source='utilisateur.email', read_only=True)
    video_url = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    validation = serializers.SerializerMethodField()

    class Meta:
        model = SoumissionActivite
        fields = [
            'id', 'defi_id', 'defi_titre',
            'utilisateur_id', 'utilisateur_nom', 'utilisateur_email',
            'rapport', 'date_activite', 'lieu', 'nombre_personnes_sensibilisees',
            'video_url', 'photos', 'statut', 'validation',
            'soumis_le', 'modifie_le', 'traitee_le',
        ]

    def get_utilisateur_nom(self, obj):
        return nom_utilisateur(obj.utilisateur)

    def get_video_url(self, obj):
        return build_file_url(self.context.get('request'), obj.video)

    def get_photos(self, obj):
        return PhotoSoumissionSerializer(
            obj.photos.all(),
            many=True,
            context={'request': self.context.get('request')},
        ).data

    def get_validation(self, obj):
        try:
            validation = obj.validation
        except Validation.DoesNotExist:
            return None
        return ValidationSerializer(validation).data


class DefiListeSerializer(serializers.ModelSerializer):
    module_id = serializers.IntegerField(source='module.id', read_only=True, allow_null=True)
    module_titre = serializers.CharField(source='module.titre', read_only=True, allow_null=True)
    image_couverture_url = serializers.SerializerMethodField()
    est_accessible = serializers.BooleanField(read_only=True)
    statut = serializers.SerializerMethodField()
    debloque_le = serializers.SerializerMethodField()
    commence_le = serializers.SerializerMethodField()
    termine_le = serializers.SerializerMethodField()
    a_soumission_en_attente = serializers.SerializerMethodField()

    class Meta:
        model = Defi
        fields = [
            'id', 'module_id', 'module_titre', 'titre', 'description',
            'image_couverture_url', 'niveau', 'ordre', 'duree_estimee',
            'points_recompense', 'nombre_photos_min', 'nombre_photos_max',
            'video_obligatoire', 'est_obligatoire', 'est_accessible',
            'statut', 'debloque_le', 'commence_le', 'termine_le',
            'a_soumission_en_attente', 'date_debut', 'date_fin',
        ]

    def _suivi(self, obj):
        suivis = self.context.get('suivis', {})
        return suivis.get(obj.id)

    def get_image_couverture_url(self, obj):
        return build_file_url(self.context.get('request'), obj.image_couverture)

    def get_statut(self, obj):
        suivi = self._suivi(obj)
        return suivi.statut if suivi else DefiUtilisateur.Statut.VERROUILLE

    def get_debloque_le(self, obj):
        suivi = self._suivi(obj)
        return suivi.debloque_le if suivi else None

    def get_commence_le(self, obj):
        suivi = self._suivi(obj)
        return suivi.commence_le if suivi else None

    def get_termine_le(self, obj):
        suivi = self._suivi(obj)
        return suivi.termine_le if suivi else None

    def get_a_soumission_en_attente(self, obj):
        utilisateur = self.context.get('utilisateur')
        if utilisateur is None:
            return False
        soumissions_en_attente = self.context.get('soumissions_en_attente')
        if soumissions_en_attente is not None:
            return obj.id in soumissions_en_attente
        return obj.soumissions.filter(
            utilisateur_id=utilisateur.id,
            statut=SoumissionActivite.Statut.EN_ATTENTE,
        ).exists()


class DefiDetailSerializer(DefiListeSerializer):
    derniere_soumission = serializers.SerializerMethodField()

    class Meta(DefiListeSerializer.Meta):
        fields = DefiListeSerializer.Meta.fields + [
            'resultat_attendu', 'criteres_validation', 'derniere_soumission',
        ]

    def get_derniere_soumission(self, obj):
        utilisateur = self.context.get('utilisateur')
        if utilisateur is None:
            return None
        soumission = obj.soumissions.filter(
            utilisateur_id=utilisateur.id
        ).select_related('utilisateur', 'defi', 'validation').prefetch_related('photos').first()
        if soumission is None:
            return None
        return SoumissionActiviteSerializer(
            soumission,
            context={'request': self.context.get('request')},
        ).data


class DefiAdminSerializer(serializers.ModelSerializer):
    module_id = serializers.IntegerField(source='module.id', read_only=True, allow_null=True)
    module_titre = serializers.CharField(source='module.titre', read_only=True, allow_null=True)
    image_couverture_url = serializers.SerializerMethodField()
    est_accessible = serializers.BooleanField(read_only=True)
    nb_participants = serializers.SerializerMethodField()
    nb_termines = serializers.SerializerMethodField()
    nb_soumissions_en_attente = serializers.SerializerMethodField()

    class Meta:
        model = Defi
        fields = [
            'id', 'module_id', 'module_titre', 'titre', 'description',
            'resultat_attendu', 'criteres_validation', 'image_couverture_url',
            'niveau', 'ordre', 'duree_estimee', 'points_recompense',
            'nombre_photos_min', 'nombre_photos_max', 'video_obligatoire',
            'est_obligatoire', 'est_actif', 'est_publie', 'est_ouvert',
            'date_debut', 'date_fin', 'est_accessible',
            'nb_participants', 'nb_termines', 'nb_soumissions_en_attente',
            'cree_le', 'modifie_le',
        ]

    def get_image_couverture_url(self, obj):
        return build_file_url(self.context.get('request'), obj.image_couverture)

    def get_nb_participants(self, obj):
        valeur = getattr(obj, 'nb_participants_annote', None)
        return valeur if valeur is not None else obj.defis_utilisateur.count()

    def get_nb_termines(self, obj):
        valeur = getattr(obj, 'nb_termines_annote', None)
        if valeur is not None:
            return valeur
        return obj.defis_utilisateur.filter(statut=DefiUtilisateur.Statut.TERMINE).count()

    def get_nb_soumissions_en_attente(self, obj):
        valeur = getattr(obj, 'nb_en_attente_annote', None)
        if valeur is not None:
            return valeur
        return obj.soumissions.filter(statut=SoumissionActivite.Statut.EN_ATTENTE).count()


class ParticipantDefiSerializer(serializers.ModelSerializer):
    utilisateur_id = serializers.IntegerField(source='utilisateur.id', read_only=True)
    utilisateur_nom = serializers.SerializerMethodField()
    utilisateur_email = serializers.EmailField(source='utilisateur.email', read_only=True)
    nb_soumissions = serializers.SerializerMethodField()
    derniere_soumission_statut = serializers.SerializerMethodField()

    class Meta:
        model = DefiUtilisateur
        fields = [
            'utilisateur_id', 'utilisateur_nom', 'utilisateur_email',
            'statut', 'debloque_le', 'commence_le', 'termine_le',
            'nb_soumissions', 'derniere_soumission_statut',
        ]

    def get_utilisateur_nom(self, obj):
        return nom_utilisateur(obj.utilisateur)

    def get_nb_soumissions(self, obj):
        return obj.defi.soumissions.filter(utilisateur_id=obj.utilisateur_id).count()

    def get_derniere_soumission_statut(self, obj):
        soumission = obj.defi.soumissions.filter(
            utilisateur_id=obj.utilisateur_id
        ).order_by('-soumis_le').first()
        return soumission.statut if soumission else None