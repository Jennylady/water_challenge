from django.urls import path

from apps.formation.views import (
    # Ambassadeur
    ListeModulesAmbassadeurView,
    DetailModuleAmbassadeurView,
    QuizModuleAmbassadeurView,
    SoumettreQuizAmbassadeurView,
    HistoriqueTentativesAmbassadeurView,
    ClassementModuleView,
    # Admin - Modules
    ListeModulesAdminView,
    CreerModuleAdminView,
    ModifierModuleAdminView,
    SupprimerModuleAdminView,
    OuvrirModuleAdminView,
    FermerModuleAdminView,
    ParticipantsModuleAdminView,
    AjouterIllustrationAdminView,
    SupprimerIllustrationAdminView,
    # Admin - Quiz
    CreerQuizAdminView,
    DetailQuizAdminView,
    ModifierQuizAdminView,
    SupprimerQuizAdminView,
)

app_name = 'formation'

urlpatterns = [
    # --- Ambassadeur ---
    path('modules/', ListeModulesAmbassadeurView.as_view(), name='liste-modules'),
    path('modules/<int:module_id>/', DetailModuleAmbassadeurView.as_view(), name='detail-module'),
    path('modules/<int:module_id>/quiz/', QuizModuleAmbassadeurView.as_view(), name='quiz-module'),
    path('modules/<int:module_id>/quiz/soumettre/', SoumettreQuizAmbassadeurView.as_view(), name='soumettre-quiz'),
    path('modules/<int:module_id>/quiz/tentatives/', HistoriqueTentativesAmbassadeurView.as_view(), name='historique-tentatives'),
    path('modules/<int:module_id>/classement/', ClassementModuleView.as_view(), name='classement-module'),

    # --- Admin : Modules ---
    path('admin/modules/', ListeModulesAdminView.as_view(), name='admin-liste-modules'),
    path('admin/modules/creer/', CreerModuleAdminView.as_view(), name='admin-creer-module'),
    path('admin/modules/<int:module_id>/modifier/', ModifierModuleAdminView.as_view(), name='admin-modifier-module'),
    path('admin/modules/<int:module_id>/supprimer/', SupprimerModuleAdminView.as_view(), name='admin-supprimer-module'),
    path('admin/modules/<int:module_id>/ouvrir/', OuvrirModuleAdminView.as_view(), name='admin-ouvrir-module'),
    path('admin/modules/<int:module_id>/fermer/', FermerModuleAdminView.as_view(), name='admin-fermer-module'),
    path('admin/modules/<int:module_id>/participants/', ParticipantsModuleAdminView.as_view(), name='admin-participants-module'),

    # --- Admin : Illustrations ---
    path('admin/modules/<int:module_id>/illustrations/', AjouterIllustrationAdminView.as_view(), name='admin-ajouter-illustration'),
    path('admin/illustrations/<int:illustration_id>/supprimer/', SupprimerIllustrationAdminView.as_view(), name='admin-supprimer-illustration'),

    # --- Admin : Quiz ---
    path('admin/modules/<int:module_id>/quiz/creer/', CreerQuizAdminView.as_view(), name='admin-creer-quiz'),
    path('admin/quiz/<int:quiz_id>/', DetailQuizAdminView.as_view(), name='admin-detail-quiz'),
    path('admin/quiz/<int:quiz_id>/modifier/', ModifierQuizAdminView.as_view(), name='admin-modifier-quiz'),
    path('admin/quiz/<int:quiz_id>/supprimer/', SupprimerQuizAdminView.as_view(), name='admin-supprimer-quiz'),
]