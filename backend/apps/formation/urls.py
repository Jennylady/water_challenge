from django.urls import path

from .views import (
    AjouterIllustrationAdminView,
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
    SupprimerModuleAdminView,
    SupprimerQuestionAdminView,
    SupprimerQuizAdminView,
)

app_name = 'formation'

urlpatterns = [
    # Ambassadeur
    path('modules/', ListeModulesAmbassadeurView.as_view(), name='liste-modules'),
    path('progression/', MaProgressionFormationView.as_view(), name='ma-progression'),
    path('modules/<uuid:module_id>/', DetailModuleAmbassadeurView.as_view(), name='detail-module'),
    path('modules/<uuid:module_id>/lire/', MarquerModuleLuView.as_view(), name='marquer-module-lu'),
    path('modules/<uuid:module_id>/quiz/', QuizModuleAmbassadeurView.as_view(), name='quiz-module'),
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
        'modules/<uuid:module_id>/quiz/tentatives/',
        HistoriqueTentativesAmbassadeurView.as_view(),
        name='historique-tentatives',
    ),
    path(
        'modules/<uuid:module_id>/classement/',
        ClassementModuleView.as_view(),
        name='classement-module',
    ),

    # Admin - modules
    path('admin/modules/', ListeModulesAdminView.as_view(), name='admin-liste-modules'),
    path('admin/modules/creer/', CreerModuleAdminView.as_view(), name='admin-creer-module'),
    path('admin/modules/<uuid:module_id>/modifier/', ModifierModuleAdminView.as_view(), name='admin-modifier-module'),
    path('admin/modules/<uuid:module_id>/supprimer/', SupprimerModuleAdminView.as_view(), name='admin-supprimer-module'),
    path('admin/modules/<uuid:module_id>/ouvrir/', OuvrirModuleAdminView.as_view(), name='admin-ouvrir-module'),
    path('admin/modules/<uuid:module_id>/fermer/', FermerModuleAdminView.as_view(), name='admin-fermer-module'),
    path('admin/modules/<uuid:module_id>/participants/', ParticipantsModuleAdminView.as_view(), name='admin-participants-module'),

    # Admin - illustrations
    path('admin/modules/<uuid:module_id>/illustrations/', AjouterIllustrationAdminView.as_view(), name='admin-ajouter-illustration'),
    path('admin/illustrations/<uuid:illustration_id>/supprimer/', SupprimerIllustrationAdminView.as_view(), name='admin-supprimer-illustration'),

    # Admin - quiz et banque de questions
    path('admin/modules/<uuid:module_id>/quiz/creer/', CreerQuizAdminView.as_view(), name='admin-creer-quiz'),
    path('admin/quiz/<uuid:quiz_id>/', DetailQuizAdminView.as_view(), name='admin-detail-quiz'),
    path('admin/quiz/<uuid:quiz_id>/modifier/', ModifierQuizAdminView.as_view(), name='admin-modifier-quiz'),
    path('admin/quiz/<uuid:quiz_id>/supprimer/', SupprimerQuizAdminView.as_view(), name='admin-supprimer-quiz'),
    path('admin/quiz/<uuid:quiz_id>/questions/ajouter/', AjouterQuestionsBanqueAdminView.as_view(), name='admin-ajouter-questions'),
    path('admin/questions/<uuid:question_id>/modifier/', ModifierQuestionAdminView.as_view(), name='admin-modifier-question'),
    path('admin/questions/<uuid:question_id>/supprimer/', SupprimerQuestionAdminView.as_view(), name='admin-supprimer-question'),
]
