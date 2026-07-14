from django.contrib import admin
from django.db import transaction
from django.utils import timezone
from django.utils.html import format_html

from apps.challenges.models import (
    Defi,
    DefiUtilisateur,
    SoumissionActivite,
    PhotoSoumission,
    Validation,
)
from apps.accounts.user.models import Profile


def apercu_fichier(fichier, hauteur=50):
    """Affiche un <img> pour un champ image, ou un tiret si vide."""
    if not fichier:
        return '—'
    try:
        url = fichier.url
    except ValueError:
        return '—'
    return format_html('<img src="{}" style="height:{}px;border-radius:4px;" />', url, hauteur)


def apercu_lien_fichier(fichier, libelle='Voir le fichier'):
    """Affiche un lien cliquable pour un fichier non-image (ex: vidéo)."""
    if not fichier:
        return '—'
    try:
        url = fichier.url
    except ValueError:
        return '—'
    return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', url, libelle)


# ---------------------------------------------------------------------------
# Logique métier partagée avec les vues (validation / refus d'une soumission)
# ---------------------------------------------------------------------------

def _valider_soumission(soumission, validateur, points_attribues, commentaire=None):
    with transaction.atomic():
        validation = Validation.objects.create(
            soumission=soumission,
            validateur=validateur,
            decision=Validation.Decision.ACCEPTEE,
            commentaire=commentaire,
            points_attribues=points_attribues,
        )
        soumission.statut = SoumissionActivite.Statut.VALIDEE
        soumission.traitee_le = timezone.now()
        soumission.save(update_fields=['statut', 'traitee_le'])

        progression, _ = DefiUtilisateur.objects.get_or_create(
            utilisateur_id=soumission.utilisateur_id, defi=soumission.defi,
            defaults={'statut': DefiUtilisateur.Statut.EN_COURS},
        )
        progression.statut = DefiUtilisateur.Statut.TERMINE
        progression.termine_le = timezone.now()
        progression.save(update_fields=['statut', 'termine_le'])

        if not validation.points_appliques:
            profile = Profile.objects.filter(user_id=soumission.utilisateur_id).first()
            if profile is not None:
                profile.points = profile.points + points_attribues
                profile.save(update_fields=['points'])
                profile.update_level()
            validation.points_appliques = True
            validation.save(update_fields=['points_appliques'])

    return validation


def _refuser_soumission(soumission, validateur, commentaire):
    with transaction.atomic():
        validation = Validation.objects.create(
            soumission=soumission,
            validateur=validateur,
            decision=Validation.Decision.REFUSEE,
            commentaire=commentaire,
            points_attribues=0,
        )
        soumission.statut = SoumissionActivite.Statut.REFUSEE
        soumission.traitee_le = timezone.now()
        soumission.save(update_fields=['statut', 'traitee_le'])
        # Le défi redevient "en_cours" pour permettre une nouvelle soumission.
        DefiUtilisateur.objects.filter(
            utilisateur_id=soumission.utilisateur_id, defi=soumission.defi,
        ).update(statut=DefiUtilisateur.Statut.EN_COURS)
    return validation


# ---------------------------------------------------------------------------
# Défi
# ---------------------------------------------------------------------------

@admin.register(Defi)
class DefiAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'module', 'niveau', 'ordre', 'apercu_image', 'points_recompense',
        'est_obligatoire', 'video_obligatoire', 'est_actif', 'est_publie', 'est_ouvert',
        'est_accessible_badge', 'nb_participants', 'date_debut', 'date_fin', 'cree_le',
    ]
    list_display_links = ['titre']
    list_editable = ['ordre', 'points_recompense', 'est_actif', 'est_publie', 'est_ouvert']
    list_filter = [
        'niveau', 'est_actif', 'est_publie', 'est_ouvert', 'est_obligatoire',
        'video_obligatoire', 'module',
    ]
    search_fields = ['titre', 'description', 'resultat_attendu', 'module__titre']
    autocomplete_fields = ['module']
    date_hierarchy = 'cree_le'
    readonly_fields = ['cree_le', 'modifie_le', 'apercu_image_grande']
    actions = [
        'action_activer', 'action_desactiver',
        'action_publier', 'action_depublier',
        'action_ouvrir', 'action_fermer',
    ]

    fieldsets = (
        (None, {'fields': ('titre', 'module', 'niveau', 'ordre', 'duree_estimee')}),
        ('Contenu', {'fields': (
            'description', 'resultat_attendu', 'criteres_validation',
            'image_couverture', 'apercu_image_grande',
        )}),
        ('Preuves attendues', {'fields': ('nombre_photos_min', 'nombre_photos_max', 'video_obligatoire')}),
        ('Récompense', {'fields': ('points_recompense', 'est_obligatoire')}),
        ('Ouverture / fermeture', {'fields': ('est_actif', 'est_publie', 'est_ouvert', 'date_debut', 'date_fin')}),
        ('Horodatage', {'fields': ('cree_le', 'modifie_le')}),
    )

    @admin.display(description='Image')
    def apercu_image(self, obj):
        return apercu_fichier(obj.image_couverture, hauteur=40)

    @admin.display(description="Aperçu de l'image de couverture")
    def apercu_image_grande(self, obj):
        return apercu_fichier(obj.image_couverture, hauteur=220)

    @admin.display(description='Accessible', boolean=True)
    def est_accessible_badge(self, obj):
        return obj.est_accessible

    @admin.display(description='Participants')
    def nb_participants(self, obj):
        return obj.defis_utilisateur.count()

    @admin.action(description='Activer les défis sélectionnés')
    def action_activer(self, request, queryset):
        nb = queryset.update(est_actif=True)
        self.message_user(request, f'{nb} défi(s) activé(s).')

    @admin.action(description='Désactiver les défis sélectionnés')
    def action_desactiver(self, request, queryset):
        nb = queryset.update(est_actif=False)
        self.message_user(request, f'{nb} défi(s) désactivé(s).')

    @admin.action(description='Publier les défis sélectionnés')
    def action_publier(self, request, queryset):
        nb = queryset.update(est_publie=True)
        self.message_user(request, f'{nb} défi(s) publié(s).')

    @admin.action(description='Dépublier les défis sélectionnés')
    def action_depublier(self, request, queryset):
        nb = queryset.update(est_publie=False)
        self.message_user(request, f'{nb} défi(s) dépublié(s).')

    @admin.action(description='Ouvrir les défis sélectionnés (accessibles)')
    def action_ouvrir(self, request, queryset):
        nb = queryset.update(est_ouvert=True)
        self.message_user(request, f'{nb} défi(s) ouvert(s).')

    @admin.action(description='Fermer les défis sélectionnés (bloqués)')
    def action_fermer(self, request, queryset):
        nb = queryset.update(est_ouvert=False)
        self.message_user(request, f'{nb} défi(s) fermé(s).')


# ---------------------------------------------------------------------------
# Défi utilisateur (progression / participants)
# ---------------------------------------------------------------------------

@admin.register(DefiUtilisateur)
class DefiUtilisateurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'defi', 'statut', 'debloque_le', 'commence_le', 'termine_le', 'modifie_le']
    list_filter = ['statut', 'defi__niveau', 'defi']
    search_fields = [
        'utilisateur__email', 'utilisateur__first_name', 'utilisateur__last_name', 'defi__titre',
    ]
    autocomplete_fields = ['defi']
    date_hierarchy = 'modifie_le'
    actions = ['action_debloquer', 'action_verrouiller']

    @admin.action(description='Débloquer manuellement (-> disponible)')
    def action_debloquer(self, request, queryset):
        nb = queryset.exclude(statut=DefiUtilisateur.Statut.TERMINE).update(
            statut=DefiUtilisateur.Statut.DISPONIBLE, debloque_le=timezone.now(),
        )
        self.message_user(request, f'{nb} défi(s) débloqué(s) manuellement.')

    @admin.action(description='Verrouiller manuellement')
    def action_verrouiller(self, request, queryset):
        nb = queryset.exclude(statut=DefiUtilisateur.Statut.TERMINE).update(
            statut=DefiUtilisateur.Statut.VERROUILLE, debloque_le=None,
        )
        self.message_user(request, f'{nb} défi(s) verrouillé(s) manuellement.')


# ---------------------------------------------------------------------------
# Photos / Validation (inlines dans SoumissionActivite)
# ---------------------------------------------------------------------------

class PhotoSoumissionInline(admin.TabularInline):
    model = PhotoSoumission
    extra = 0
    fields = ['apercu', 'image', 'ordre']
    readonly_fields = ['apercu']
    ordering = ['ordre']

    @admin.display(description='Aperçu')
    def apercu(self, obj):
        return apercu_fichier(obj.image, hauteur=80)


class ValidationInline(admin.StackedInline):
    model = Validation
    extra = 0
    max_num = 1
    can_delete = False
    readonly_fields = ['validateur', 'decision', 'commentaire', 'points_attribues', 'points_appliques', 'valide_le']

    def has_add_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# Soumission d'activité (file de validation)
# ---------------------------------------------------------------------------

@admin.register(SoumissionActivite)
class SoumissionActiviteAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'defi', 'date_activite', 'lieu', 'nombre_personnes_sensibilisees',
        'statut', 'apercu_video', 'nb_photos', 'soumis_le', 'traitee_le',
    ]
    list_filter = ['statut', 'defi__niveau', 'defi']
    search_fields = ['utilisateur__email', 'defi__titre', 'lieu', 'rapport']
    date_hierarchy = 'soumis_le'
    readonly_fields = [
        'utilisateur', 'defi', 'rapport', 'date_activite', 'lieu',
        'nombre_personnes_sensibilisees', 'apercu_video_grand',
        'soumis_le', 'modifie_le', 'traitee_le',
    ]
    inlines = [PhotoSoumissionInline, ValidationInline]
    actions = ['action_valider', 'action_refuser']

    fieldsets = (
        (None, {'fields': ('utilisateur', 'defi', 'statut')}),
        ('Rapport de l\'ambassadeur', {'fields': (
            'rapport', 'date_activite', 'lieu', 'nombre_personnes_sensibilisees', 'apercu_video_grand',
        )}),
        ('Horodatage', {'fields': ('soumis_le', 'modifie_le', 'traitee_le')}),
    )

    @admin.display(description='Vidéo')
    def apercu_video(self, obj):
        return apercu_lien_fichier(obj.video, libelle='Vidéo')

    @admin.display(description='Vidéo jointe')
    def apercu_video_grand(self, obj):
        return apercu_lien_fichier(obj.video, libelle='Voir la vidéo soumise')

    @admin.display(description='Photos')
    def nb_photos(self, obj):
        return obj.photos.count()

    @admin.action(description="Valider les soumissions sélectionnées (en attente uniquement, points du défi appliqués)")
    def action_valider(self, request, queryset):
        nb_traitees = 0
        for soumission in queryset.select_related('defi', 'utilisateur'):
            if soumission.statut != SoumissionActivite.Statut.EN_ATTENTE:
                continue
            _valider_soumission(
                soumission,
                validateur=request.user,
                points_attribues=soumission.defi.points_recompense,
                commentaire='Validée en masse depuis l’admin.',
            )
            nb_traitees += 1
        self.message_user(request, f'{nb_traitees} soumission(s) validée(s), points attribués.')

    @admin.action(description="Refuser les soumissions sélectionnées (en attente uniquement)")
    def action_refuser(self, request, queryset):
        nb_traitees = 0
        for soumission in queryset.select_related('defi', 'utilisateur'):
            if soumission.statut != SoumissionActivite.Statut.EN_ATTENTE:
                continue
            _refuser_soumission(
                soumission, validateur=request.user, commentaire='Refusée en masse depuis l’admin.',
            )
            nb_traitees += 1
        self.message_user(request, f'{nb_traitees} soumission(s) refusée(s).')

    def has_add_permission(self, request):
        # Les soumissions sont créées uniquement par les ambassadeurs via l'API.
        return False


# ---------------------------------------------------------------------------
# Validation (journal en lecture seule)
# ---------------------------------------------------------------------------

@admin.register(Validation)
class ValidationAdmin(admin.ModelAdmin):
    list_display = ['soumission', 'validateur', 'decision', 'points_attribues', 'points_appliques', 'valide_le']
    list_filter = ['decision', 'points_appliques']
    search_fields = ['soumission__utilisateur__email', 'soumission__defi__titre']
    readonly_fields = [
        'soumission', 'validateur', 'decision', 'points_attribues', 'points_appliques', 'valide_le',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False