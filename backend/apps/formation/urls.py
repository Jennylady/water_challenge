from django.urls import path

from .views import (
    AjouterIllustrationAdminView,
    AjouterRessourcesModuleAdminView,
    AjouterQuestionsBanqueAdminView,
    ClassementModuleView,
    CreerModuleAdminView,
    CreerQuizAdminView,
    DetailModuleAmbassadeurView,
    DetailQuizAdminView,
    FermerModuleAdminView,
    HistoriqueTentativesAmbassadeurView,
    ListeModulesAdminView,
    ListeModulesAmbassadeurView,
    MarquerModuleLuView,
    MaProgressionFormationView,
    ModifierModuleAdminView,
    ModifierQuestionAdminView,
    ModifierQuizAdminView,
    OuvrirModuleAdminView,
    ParticipantsModuleAdminView,
    QuizModuleAmbassadeurView,
    RepondreQuestionAmbassadeurView,
    SoumettreTentativeQuizAmbassadeurView,
    SupprimerIllustrationAdminView,
    SupprimerRessourceModuleAdminView,
    SupprimerModuleAdminView,
    SupprimerQuestionAdminView,
    SupprimerQuizAdminView,
)

app_name = 'formation'

urlpatterns = [
    # Ambassadeur
    path('modules/', ListeModulesAmbassadeurView.as_view(), name='liste-modules'),
    path('progression/', MaProgressionFormationView.as_view(), name='ma-progression'),
    path('modules/<slug:module_slug>/', DetailModuleAmbassadeurView.as_view(), name='detail-module'),
    path('modules/<slug:module_slug>/lire/', MarquerModuleLuView.as_view(), name='marquer-module-lu'),
    path('modules/<slug:module_slug>/quiz/', QuizModuleAmbassadeurView.as_view(), name='quiz-module'),
    path(
        'quiz/tentatives/<uuid:tentative_id>/questions/<uuid:question_id>/reponse/',
        RepondreQuestionAmbassadeurView.as_view(),
        name='repondre-question',
    ),
    path(
        'quiz/tentatives/<uuid:tentative_id>/soumettre/',
        SoumettreTentativeQuizAmbassadeurView.as_view(),
        name='soumettre-tentative',
    ),
    path(
        'modules/<slug:module_slug>/quiz/tentatives/',
        HistoriqueTentativesAmbassadeurView.as_view(),
        name='historique-tentatives',
    ),
    path(
        'modules/<slug:module_slug>/classement/',
        ClassementModuleView.as_view(),
        name='classement-module',
    ),

    # Admin - modules
    path('admin/modules/', ListeModulesAdminView.as_view(), name='admin-liste-modules'),
    path('admin/modules/creer/', CreerModuleAdminView.as_view(), name='admin-creer-module'),
    path('admin/modules/<slug:module_slug>/modifier/', ModifierModuleAdminView.as_view(), name='admin-modifier-module'),
    path('admin/modules/<slug:module_slug>/supprimer/', SupprimerModuleAdminView.as_view(), name='admin-supprimer-module'),
    path('admin/modules/<slug:module_slug>/ouvrir/', OuvrirModuleAdminView.as_view(), name='admin-ouvrir-module'),
    path('admin/modules/<slug:module_slug>/fermer/', FermerModuleAdminView.as_view(), name='admin-fermer-module'),
    path('admin/modules/<slug:module_slug>/participants/', ParticipantsModuleAdminView.as_view(), name='admin-participants-module'),

    # Admin - illustrations
    path('admin/modules/<slug:module_slug>/illustrations/', AjouterIllustrationAdminView.as_view(), name='admin-ajouter-illustration'),
    path('admin/illustrations/<uuid:illustration_id>/supprimer/', SupprimerIllustrationAdminView.as_view(), name='admin-supprimer-illustration'),
    path('admin/modules/<slug:module_slug>/ressources/', AjouterRessourcesModuleAdminView.as_view(), name='admin-ajouter-ressources'),
    path('admin/ressources/<int:ressource_id>/supprimer/', SupprimerRessourceModuleAdminView.as_view(), name='admin-supprimer-ressource'),

    # Admin - quiz et banque de questions
    path('admin/modules/<slug:module_slug>/quiz/creer/', CreerQuizAdminView.as_view(), name='admin-creer-quiz'),
    path('admin/quiz/<uuid:quiz_id>/', DetailQuizAdminView.as_view(), name='admin-detail-quiz'),
    path('admin/quiz/<uuid:quiz_id>/modifier/', ModifierQuizAdminView.as_view(), name='admin-modifier-quiz'),
    path('admin/quiz/<uuid:quiz_id>/supprimer/', SupprimerQuizAdminView.as_view(), name='admin-supprimer-quiz'),
    path('admin/quiz/<uuid:quiz_id>/questions/ajouter/', AjouterQuestionsBanqueAdminView.as_view(), name='admin-ajouter-questions'),
    path('admin/questions/<uuid:question_id>/modifier/', ModifierQuestionAdminView.as_view(), name='admin-modifier-question'),
    path('admin/questions/<uuid:question_id>/supprimer/', SupprimerQuestionAdminView.as_view(), name='admin-supprimer-question'),
]
