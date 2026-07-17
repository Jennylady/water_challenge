from django.urls import path

from .views import (
    AnnulerSoumissionAmbassadeurView,
    CommencerDefiAmbassadeurView,
    CreerDefiAdminView,
    DetailDefiAmbassadeurView,
    DefisPopulairesPublicView,
    DetailSoumissionAdminView,
    DetailSoumissionAmbassadeurView,
    FermerDefiAdminView,
    ListeDefisAdminView,
    ListeDefisAmbassadeurView,
    ListeSoumissionsAdminView,
    MesSoumissionsAmbassadeurView,
    MesStatistiquesDefisView,
    ModifierDefiAdminView,
    OuvrirDefiAdminView,
    ParticipantsDefiAdminView,
    SoumettreActiviteAmbassadeurView,
    StatistiquesChallengesAdminView,
    SupprimerDefiAdminView,
    ValiderSoumissionAdminView,
)

app_name = 'challenges'

urlpatterns = [
    # --- Public : landing page ---
    path('defis/populaires/', DefisPopulairesPublicView.as_view(), name='defis-populaires'),

    # --- Ambassadeur : défis ---
    path('defis/', ListeDefisAmbassadeurView.as_view(), name='liste-defis'),
    path('defis/<int:defi_id>/', DetailDefiAmbassadeurView.as_view(), name='detail-defi'),
    path('defis/<int:defi_id>/commencer/', CommencerDefiAmbassadeurView.as_view(), name='commencer-defi'),
    path('defis/<int:defi_id>/soumettre/', SoumettreActiviteAmbassadeurView.as_view(), name='soumettre-activite'),

    # --- Ambassadeur : activités ---
    path('mes-soumissions/', MesSoumissionsAmbassadeurView.as_view(), name='mes-soumissions'),
    path('mes-soumissions/<int:soumission_id>/', DetailSoumissionAmbassadeurView.as_view(), name='detail-soumission'),
    path('mes-soumissions/<int:soumission_id>/annuler/', AnnulerSoumissionAmbassadeurView.as_view(), name='annuler-soumission'),
    path('mes-statistiques/', MesStatistiquesDefisView.as_view(), name='mes-statistiques'),

    # --- Admin : gestion des défis ---
    path('admin/defis/', ListeDefisAdminView.as_view(), name='admin-liste-defis'),
    path('admin/defis/creer/', CreerDefiAdminView.as_view(), name='admin-creer-defi'),
    path('admin/defis/<int:defi_id>/modifier/', ModifierDefiAdminView.as_view(), name='admin-modifier-defi'),
    path('admin/defis/<int:defi_id>/supprimer/', SupprimerDefiAdminView.as_view(), name='admin-supprimer-defi'),
    path('admin/defis/<int:defi_id>/ouvrir/', OuvrirDefiAdminView.as_view(), name='admin-ouvrir-defi'),
    path('admin/defis/<int:defi_id>/fermer/', FermerDefiAdminView.as_view(), name='admin-fermer-defi'),
    path('admin/defis/<int:defi_id>/participants/', ParticipantsDefiAdminView.as_view(), name='admin-participants-defi'),

    # --- Admin / Validateur : soumissions ---
    path('admin/soumissions/', ListeSoumissionsAdminView.as_view(), name='admin-liste-soumissions'),
    path('admin/soumissions/<int:soumission_id>/', DetailSoumissionAdminView.as_view(), name='admin-detail-soumission'),
    path('admin/soumissions/<int:soumission_id>/valider/', ValiderSoumissionAdminView.as_view(), name='admin-valider-soumission'),
    path('admin/statistiques/', StatistiquesChallengesAdminView.as_view(), name='admin-statistiques'),
]