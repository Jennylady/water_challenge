from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Choix,
    IllustrationModule,
    ImageIllustrationModule,
    RessourceModule,
    Module,
    ProgressionModule,
    Question,
    QuestionTentative,
    Quiz,
    ReponseQuiz,
    TentativeQuiz,
)


def apercu_fichier(fichier, hauteur=50):
    if not fichier:
        return '—'
    try:
        url = fichier.url
    except ValueError:
        return '—'
    return format_html('<img src="{}" style="height:{}px;border-radius:4px;" />', url, hauteur)


class ImageIllustrationModuleInline(admin.TabularInline):
    model = ImageIllustrationModule
    extra = 1
    fields = ['uuid', 'apercu', 'image', 'ordre']
    readonly_fields = ['uuid', 'apercu']
    ordering = ['ordre']

    @admin.display(description='Aperçu')
    def apercu(self, obj):
        return apercu_fichier(obj.image, hauteur=60)


@admin.register(IllustrationModule)
class IllustrationModuleAdmin(admin.ModelAdmin):
    list_display = ['titre', 'module', 'ordre', 'nombre_images']
    search_fields = ['titre', 'description', 'module__titre']
    list_filter = ['module']
    ordering = ['module', 'ordre']
    readonly_fields = ['uuid']
    inlines = [ImageIllustrationModuleInline]

    @admin.display(description='Images')
    def nombre_images(self, obj):
        return obj.images.count()


class RessourceModuleInline(admin.TabularInline):
    model = RessourceModule
    extra = 1
    fields = ['fichier']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'uuid', 'niveau', 'ordre', 'apercu_image', 'est_publie', 'est_ouvert',
        'est_accessible_badge', 'a_un_quiz_badge', 'nb_participants', 'cree_le',
    ]
    list_display_links = ['titre']
    list_editable = ['ordre', 'est_publie', 'est_ouvert']
    list_filter = ['niveau', 'est_publie', 'est_ouvert']
    search_fields = ['titre', 'uuid', 'slug', 'contenu', 'resume']
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ['uuid', 'cree_le', 'modifie_le', 'apercu_image_grande']
    date_hierarchy = 'cree_le'
    inlines = [RessourceModuleInline]
    actions = ['action_publier', 'action_depublier', 'action_ouvrir', 'action_fermer']

    fieldsets = (
        ('Identité', {'fields': ('uuid', 'titre', 'slug', 'niveau', 'ordre')}),
        ('Contenu', {'fields': ('resume', 'contenu', 'video', 'image_couverture', 'apercu_image_grande')}),
        ('Ouverture', {'fields': ('est_publie', 'est_ouvert', 'date_debut', 'date_fin')}),
        ('Horodatage', {'fields': ('cree_le', 'modifie_le')}),
    )

    @admin.display(description='Image')
    def apercu_image(self, obj):
        return apercu_fichier(obj.image_couverture, hauteur=40)

    @admin.display(description='Aperçu de la couverture')
    def apercu_image_grande(self, obj):
        return apercu_fichier(obj.image_couverture, hauteur=220)

    @admin.display(description='Accessible', boolean=True)
    def est_accessible_badge(self, obj):
        return obj.est_accessible

    @admin.display(description='Quiz', boolean=True)
    def a_un_quiz_badge(self, obj):
        return hasattr(obj, 'quiz')

    @admin.display(description='Participants')
    def nb_participants(self, obj):
        return obj.progressions.count()

    @admin.action(description='Publier les modules sélectionnés')
    def action_publier(self, request, queryset):
        self.message_user(request, f'{queryset.update(est_publie=True)} module(s) publié(s).')

    @admin.action(description='Dépublier les modules sélectionnés')
    def action_depublier(self, request, queryset):
        self.message_user(request, f'{queryset.update(est_publie=False)} module(s) dépublié(s).')

    @admin.action(description='Ouvrir les modules sélectionnés')
    def action_ouvrir(self, request, queryset):
        self.message_user(request, f'{queryset.update(est_ouvert=True)} module(s) ouvert(s).')

    @admin.action(description='Fermer les modules sélectionnés')
    def action_fermer(self, request, queryset):
        self.message_user(request, f'{queryset.update(est_ouvert=False)} module(s) fermé(s).')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ['uuid', 'texte', 'type_question', 'points', 'ordre']
    readonly_fields = ['uuid']
    ordering = ['ordre']
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'uuid', 'module', 'score_de_reussite', 'correction_automatique',
        'nombre_questions', 'nombre_questions_banque_display', 'points_total_banque_display',
    ]
    list_filter = ['correction_automatique', 'module__niveau']
    search_fields = ['titre', 'uuid', 'module__titre', 'module__uuid']
    autocomplete_fields = ['module']
    readonly_fields = ['uuid', 'nombre_questions_banque_display', 'points_total_banque_display']
    inlines = [QuestionInline]

    @admin.display(description='Questions en banque')
    def nombre_questions_banque_display(self, obj):
        return obj.nombre_questions_banque

    @admin.display(description='Points de la banque')
    def points_total_banque_display(self, obj):
        return obj.points_total_banque


class ChoixInline(admin.TabularInline):
    model = Choix
    extra = 1
    fields = ['uuid', 'texte', 'est_correct', 'explication']
    readonly_fields = ['uuid']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'texte', 'uuid', 'quiz', 'type_question', 'points', 'ordre',
        'nb_choix', 'nb_choix_corrects', 'nb_tirages',
    ]
    list_editable = ['points', 'ordre']
    list_filter = ['type_question', 'quiz__module__niveau']
    search_fields = ['texte', 'uuid', 'quiz__titre', 'quiz__module__titre']
    autocomplete_fields = ['quiz']
    readonly_fields = ['uuid', 'nb_tirages']
    inlines = [ChoixInline]

    @admin.display(description='Choix')
    def nb_choix(self, obj):
        return obj.choix.count()

    @admin.display(description='Choix corrects')
    def nb_choix_corrects(self, obj):
        return obj.choix.filter(est_correct=True).count()

    @admin.display(description='Tentatives utilisant cette question')
    def nb_tirages(self, obj):
        return obj.tirages.count()


@admin.register(ProgressionModule)
class ProgressionModuleAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'module', 'est_lu', 'lu_le', 'est_termine', 'termine_le']
    list_filter = ['est_lu', 'est_termine', 'module__niveau']
    search_fields = ['utilisateur__email', 'module__titre', 'module__uuid']
    autocomplete_fields = ['module']
    date_hierarchy = 'lu_le'
    actions = ['action_reinitialiser']

    @admin.action(description='Réinitialiser les progressions sélectionnées')
    def action_reinitialiser(self, request, queryset):
        nombre = queryset.update(est_lu=False, lu_le=None, est_termine=False, termine_le=None)
        self.message_user(request, f'{nombre} progression(s) réinitialisée(s).')


class QuestionTentativeInline(admin.TabularInline):
    model = QuestionTentative
    extra = 0
    can_delete = False
    fields = ['ordre', 'question']
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


class ReponseQuizInline(admin.TabularInline):
    model = ReponseQuiz
    extra = 0
    can_delete = False
    fields = [
        'uuid', 'question', 'choix_selectionnes_display', 'reponse_texte',
        'est_correcte', 'points_obtenus', 'modifiee_le',
    ]
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='Choix sélectionnés')
    def choix_selectionnes_display(self, obj):
        return ', '.join(c.texte for c in obj.choix_selectionnes.all()) or '—'


@admin.register(TentativeQuiz)
class TentativeQuizAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'quiz', 'uuid', 'statut', 'score', 'points_obtenus',
        'points_total', 'est_reussi', 'cree_le', 'soumise_le',
    ]
    list_filter = ['statut', 'est_reussi', 'quiz__module__niveau']
    search_fields = ['uuid', 'utilisateur__email', 'quiz__titre']
    date_hierarchy = 'cree_le'
    inlines = [QuestionTentativeInline, ReponseQuizInline]
    readonly_fields = [
        'uuid', 'utilisateur', 'quiz', 'statut', 'score', 'points_obtenus',
        'points_total', 'est_reussi', 'cree_le', 'soumise_le',
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Choix)
class ChoixAdmin(admin.ModelAdmin):
    list_display = ['texte', 'uuid', 'question', 'est_correct']
    list_filter = ['est_correct', 'question__type_question']
    search_fields = ['texte', 'uuid', 'question__texte']
    autocomplete_fields = ['question']
    readonly_fields = ['uuid']