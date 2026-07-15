from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


UUID = openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID)
SLUG = openapi.Schema(type=openapi.TYPE_STRING)
NIVEAUX_MODULE = ['débutant', 'apprenti', 'actif', 'leader']
DATE_TIME = openapi.Schema(
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATETIME,
)
DATE_TIME_NULLABLE = openapi.Schema(
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATETIME,
    x_nullable=True,
)
NULL_OBJECT = openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)


def enveloppe(nom, schema, avec_message=True):
    properties = {'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)}
    if avec_message:
        properties['message'] = openapi.Schema(type=openapi.TYPE_STRING)
    properties[nom] = schema
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=properties)


ERREUR = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'erreur': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

PROGRESSION = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'pourcentage': openapi.Schema(type=openapi.TYPE_INTEGER),
        'lecture': openapi.Schema(type=openapi.TYPE_INTEGER),
        'quiz': openapi.Schema(type=openapi.TYPE_INTEGER),
        'challenges': openapi.Schema(type=openapi.TYPE_INTEGER),
        'challenges_termines': openapi.Schema(type=openapi.TYPE_INTEGER),
        'est_termine': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

IMAGE_ILLUSTRATION = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'image': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

ILLUSTRATION = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'images': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=IMAGE_ILLUSTRATION,
        ),
    },
)

RESSOURCE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'fichier': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

CHOIX_PUBLIC = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

REPONSE_ENREGISTREE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    x_nullable=True,
    properties={
        'choix_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=UUID),
        'reponse_texte': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

QUESTION_PUBLIC = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
        'type_question': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=['choix_unique', 'choix_multiple', 'reponse_courte'],
        ),
        'points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'choix': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=CHOIX_PUBLIC,
            description="Absent pour une question de type reponse_courte.",
        ),
        'reponse_enregistree': REPONSE_ENREGISTREE,
    },
)

QUIZ_PUBLIC = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'module_slug': SLUG,
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'correction_automatique': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'tentative_id': UUID,
        'statut_tentative': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=['en_cours', 'soumise'],
        ),
        'questions_repondues': openapi.Schema(type=openapi.TYPE_INTEGER),
        'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_PUBLIC),
    },
)

CHOIX_ADMIN = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
        'est_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'explication': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    },
)

QUESTION_ADMIN = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
        'type_question': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=['choix_unique', 'choix_multiple', 'reponse_courte'],
        ),
        'points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'explication': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'choix': openapi.Schema(type=openapi.TYPE_ARRAY, items=CHOIX_ADMIN),
        'reponses_acceptees': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
        ),
        'sensible_a_la_casse': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

CHOIX_INPUT = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['texte'],
    properties={
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
        'est_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'explication': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

QUESTION_INPUT_PROPERTIES = {
    'texte': openapi.Schema(type=openapi.TYPE_STRING),
    'type_question': openapi.Schema(
        type=openapi.TYPE_STRING,
        enum=['choix_unique', 'choix_multiple', 'reponse_courte'],
    ),
    'points': openapi.Schema(type=openapi.TYPE_INTEGER, default=1),
    'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
    'explication': openapi.Schema(type=openapi.TYPE_STRING),
    'choix': openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=CHOIX_INPUT,
        description="Requis pour choix_unique et choix_multiple.",
    ),
    'reponses_acceptees': openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(type=openapi.TYPE_STRING),
        description="Requis pour reponse_courte.",
    ),
    'sensible_a_la_casse': openapi.Schema(type=openapi.TYPE_BOOLEAN),
}

QUESTION_CREATION_INPUT = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['texte'],
    properties=QUESTION_INPUT_PROPERTIES,
)
QUESTION_MODIFICATION_INPUT = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties=QUESTION_INPUT_PROPERTIES,
)

QUIZ_ADMIN = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'module_slug': SLUG,
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'correction_automatique': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'nombre_questions_banque': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_total_banque': openapi.Schema(type=openapi.TYPE_INTEGER),
        'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_ADMIN),
    },
)

MODULE_LISTE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'slug': SLUG,
        'resume': openapi.Schema(type=openapi.TYPE_STRING),
        'niveau': openapi.Schema(type=openapi.TYPE_STRING, enum=NIVEAUX_MODULE),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'image_couverture': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'date_debut': DATE_TIME_NULLABLE,
        'date_fin': DATE_TIME_NULLABLE,
        'est_accessible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_lu': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_termine': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'progression': PROGRESSION,
    },
)

MODULE_DETAIL = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        **MODULE_LISTE.properties,
        'contenu': openapi.Schema(type=openapi.TYPE_STRING),
        'video': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'illustrations': openapi.Schema(type=openapi.TYPE_ARRAY, items=ILLUSTRATION),
        'ressources': openapi.Schema(type=openapi.TYPE_ARRAY, items=RESSOURCE),
        'lu_le': DATE_TIME_NULLABLE,
        'quiz_disponible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

MODULE_ADMIN = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'slug': SLUG,
        'contenu': openapi.Schema(type=openapi.TYPE_STRING),
        'resume': openapi.Schema(type=openapi.TYPE_STRING),
        'niveau': openapi.Schema(type=openapi.TYPE_STRING, enum=NIVEAUX_MODULE),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'est_publie': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_ouvert': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'date_debut': DATE_TIME_NULLABLE,
        'date_fin': DATE_TIME_NULLABLE,
        'est_accessible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'video': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'image_couverture': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'illustrations': openapi.Schema(type=openapi.TYPE_ARRAY, items=ILLUSTRATION),
        'ressources': openapi.Schema(type=openapi.TYPE_ARRAY, items=RESSOURCE),
        'a_un_quiz': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'nb_participants': openapi.Schema(type=openapi.TYPE_INTEGER),
        'cree_le': DATE_TIME,
        'modifie_le': DATE_TIME,
    },
)

REPONSE_DETAIL = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'question_id': UUID,
        'question_texte': openapi.Schema(type=openapi.TYPE_STRING),
        'type_question': openapi.Schema(type=openapi.TYPE_STRING),
        'choix_selectionnes': openapi.Schema(type=openapi.TYPE_ARRAY, items=CHOIX_PUBLIC),
        'reponse_texte': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'est_correcte': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'points_obtenus': openapi.Schema(type=openapi.TYPE_INTEGER),
        'enregistree_le': DATE_TIME,
        'modifiee_le': DATE_TIME,
    },
)

TENTATIVE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'quiz_id': UUID,
        'module_slug': SLUG,
        'statut': openapi.Schema(type=openapi.TYPE_STRING, enum=['en_cours', 'soumise']),
        'score': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_obtenus': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_total': openapi.Schema(type=openapi.TYPE_INTEGER),
        'est_reussi': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nombre_reponses': openapi.Schema(type=openapi.TYPE_INTEGER),
        'cree_le': DATE_TIME,
        'soumise_le': DATE_TIME_NULLABLE,
        'reponses': openapi.Schema(type=openapi.TYPE_ARRAY, items=REPONSE_DETAIL),
    },
)

PARTICIPANT = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'utilisateur_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_nom': openapi.Schema(type=openapi.TYPE_STRING),
        'utilisateur_email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'est_lu': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'lu_le': DATE_TIME_NULLABLE,
        'est_termine': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'termine_le': DATE_TIME_NULLABLE,
    },
)

CLASSEMENT = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rang': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_nom': openapi.Schema(type=openapi.TYPE_STRING),
        'meilleur_score': openapi.Schema(type=openapi.TYPE_INTEGER),
        'meilleurs_points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'est_reussi': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'tentatives_effectuees': openapi.Schema(type=openapi.TYPE_INTEGER),
        'terminee_le': DATE_TIME_NULLABLE,
    },
)

REPONSE_QUESTION = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'question_id': UUID,
        'enregistree': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'modifiee_le': DATE_TIME,
        'est_correcte': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'correction': openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True),
        'explication': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

PROGRESSION_MODULE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'module_slug': SLUG,
        **PROGRESSION.properties,
    },
)

PROGRESSION_GLOBALE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'pourcentage_global': openapi.Schema(type=openapi.TYPE_INTEGER),
        'modules': openapi.Schema(type=openapi.TYPE_ARRAY, items=MODULE_LISTE),
    },
)


# =============================================================================
# Ambassadeur
# =============================================================================

swagger_liste_modules_ambassadeur = swagger_auto_schema(
    operation_summary="Lister les modules publiés",
    manual_parameters=[
        openapi.Parameter(
            'niveau', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False, enum=NIVEAUX_MODULE,
        ),
    ],
    responses={
        200: enveloppe(
            'modules',
            openapi.Schema(type=openapi.TYPE_ARRAY, items=MODULE_LISTE),
            avec_message=False,
        ),
        403: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_detail_module_ambassadeur = swagger_auto_schema(
    operation_summary="Consulter un module",
    operation_description=(
        "La consultation ne marque pas automatiquement le module comme lu. "
        "Utilisez l'endpoint /lire/ pour enregistrer la lecture."
    ),
    responses={
        200: enveloppe('module', MODULE_DETAIL, avec_message=False),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_marquer_module_lu = swagger_auto_schema(
    operation_summary="Marquer un module comme lu",
    operation_description=(
        "Ajoute 25 % à la progression. La lecture n'est pas obligatoire pour accéder au quiz."
    ),
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
    responses={
        200: enveloppe('progression', PROGRESSION_MODULE),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_ma_progression_formation = swagger_auto_schema(
    operation_summary="Consulter ma progression de formation",
    operation_description=(
        "Recalcule les modules à partir des lectures, quiz réussis et défis terminés déjà enregistrés."
    ),
    responses={
        200: enveloppe('progression', PROGRESSION_GLOBALE, avec_message=False),
        403: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_quiz_module_ambassadeur = swagger_auto_schema(
    operation_summary="Récupérer ou reprendre une tentative de quiz",
    operation_description=(
        "Le quiz est accessible indépendamment de la lecture du module. Une tentative est créée "
        "si aucune tentative en cours n'existe. Le tirage des questions est persisté."
    ),
    responses={
        200: enveloppe('quiz', QUIZ_PUBLIC),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_repondre_question = swagger_auto_schema(
    operation_summary="Enregistrer la réponse d'une question",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'choix_ids': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=UUID,
                description="Pour choix_unique ou choix_multiple.",
            ),
            'reponse_texte': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Pour reponse_courte.",
            ),
        },
    ),
    responses={
        200: enveloppe('reponse', REPONSE_QUESTION),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_soumettre_tentative = swagger_auto_schema(
    operation_summary="Soumettre et noter une tentative",
    operation_description=(
        "Vérifie que toutes les questions tirées ont une réponse, recalcule le score côté serveur "
        "et met à jour la progression en cas de réussite."
    ),
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
    responses={
        200: enveloppe('tentative', TENTATIVE),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_historique_tentatives = swagger_auto_schema(
    operation_summary="Historique des tentatives du module",
    responses={
        200: enveloppe(
            'tentatives',
            openapi.Schema(type=openapi.TYPE_ARRAY, items=TENTATIVE),
            avec_message=False,
        ),
        401: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_classement_module = swagger_auto_schema(
    operation_summary="Classement du module",
    responses={
        200: enveloppe(
            'classement',
            openapi.Schema(type=openapi.TYPE_ARRAY, items=CLASSEMENT),
            avec_message=False,
        ),
        401: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)


# =============================================================================
# Admin - modules
# =============================================================================

swagger_liste_modules_admin = swagger_auto_schema(
    operation_summary="[Admin] Lister tous les modules",
    manual_parameters=[
        openapi.Parameter(
            'niveau', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False, enum=NIVEAUX_MODULE,
        ),
        openapi.Parameter('est_publie', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False),
    ],
    responses={
        200: enveloppe(
            'modules',
            openapi.Schema(type=openapi.TYPE_ARRAY, items=MODULE_ADMIN),
            avec_message=False,
        ),
        403: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)


def _module_form_parameters(champs_requis, inclure_suppressions=False):
    parameters = [
        openapi.Parameter('titre', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('contenu', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('resume', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter(
            'niveau', openapi.IN_FORM, type=openapi.TYPE_STRING,
            required=champs_requis, enum=NIVEAUX_MODULE,
        ),
        openapi.Parameter('ordre', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('est_publie', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('est_ouvert', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter(
            'date_debut',
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            required=False,
        ),
        openapi.Parameter(
            'date_fin',
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            required=False,
        ),
        openapi.Parameter('video', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
        openapi.Parameter('image_couverture', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
    ]
    if inclure_suppressions:
        parameters.extend([
            openapi.Parameter(
                'supprimer_video',
                openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
            openapi.Parameter(
                'supprimer_image_couverture',
                openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
        ])
    return parameters


swagger_creer_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Créer un module",
    manual_parameters=_module_form_parameters(True),
    consumes=['multipart/form-data'],
    responses={
        201: enveloppe('module', MODULE_ADMIN),
        400: ERREUR,
        403: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_modifier_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Modifier un module par son slug",
    manual_parameters=_module_form_parameters(False, inclure_suppressions=True),
    consumes=['multipart/form-data'],
    responses={
        200: enveloppe('module', MODULE_ADMIN),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_supprimer_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer un module par son slug",
    responses={
        200: enveloppe('module', NULL_OBJECT),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_ouvrir_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Ouvrir un module par son slug",
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
    responses={
        200: enveloppe('module', MODULE_ADMIN),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_fermer_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Fermer un module par son slug",
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
    responses={
        200: enveloppe('module', MODULE_ADMIN),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_participants_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Participants d'un module",
    responses={
        200: enveloppe(
            'participants',
            openapi.Schema(type=openapi.TYPE_ARRAY, items=PARTICIPANT),
            avec_message=False,
        ),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_ajouter_illustration_admin = swagger_auto_schema(
    operation_summary="[Admin] Ajouter une illustration à un module",
    manual_parameters=[
        openapi.Parameter('titre', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('ordre', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(
            'images',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=True,
            description="Répéter la clé images pour envoyer plusieurs fichiers. La clé image est aussi acceptée.",
        ),
    ],
    consumes=['multipart/form-data'],
    responses={
        201: enveloppe('illustration', ILLUSTRATION),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_supprimer_illustration_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer une illustration",
    responses={
        200: enveloppe('illustration', NULL_OBJECT),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_ajouter_ressources_admin = swagger_auto_schema(
    operation_summary="[Admin] Ajouter des ressources à un module",
    manual_parameters=[
        openapi.Parameter(
            'fichiers',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=True,
            description="Répéter la clé fichiers pour envoyer plusieurs ressources. La clé fichier est aussi acceptée.",
        ),
    ],
    consumes=['multipart/form-data'],
    responses={
        201: enveloppe(
            'ressources',
            openapi.Schema(type=openapi.TYPE_ARRAY, items=RESSOURCE),
        ),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_supprimer_ressource_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer une ressource",
    responses={
        200: enveloppe('ressource', NULL_OBJECT),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)


# =============================================================================
# Admin - quiz / banque
# =============================================================================

swagger_creer_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Créer le quiz unique d'un module",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['titre'],
        properties={
            'titre': openapi.Schema(type=openapi.TYPE_STRING),
            'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER, default=50),
            'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER, default=5),
            'correction_automatique': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
            'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_CREATION_INPUT),
        },
    ),
    responses={
        201: enveloppe('quiz', QUIZ_ADMIN),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_detail_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Consulter un quiz et sa banque",
    responses={
        200: enveloppe('quiz', QUIZ_ADMIN, avec_message=False),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_modifier_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Modifier les paramètres d'un quiz",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'titre': openapi.Schema(type=openapi.TYPE_STRING),
            'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
            'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
            'correction_automatique': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_CREATION_INPUT),
        },
    ),
    responses={
        200: enveloppe('quiz', QUIZ_ADMIN),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        409: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_supprimer_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer un quiz",
    responses={
        200: enveloppe('quiz', NULL_OBJECT),
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_ajouter_questions_banque_admin = swagger_auto_schema(
    operation_summary="[Admin] Ajouter des questions à la banque",
    operation_description=(
        "Le corps peut contenir questions: [...] ou directement les champs d'une seule question."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'questions': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=QUESTION_CREATION_INPUT,
            ),
            **QUESTION_INPUT_PROPERTIES,
        },
    ),
    responses={
        201: enveloppe(
            'questions',
            openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_ADMIN),
        ),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_modifier_question_admin = swagger_auto_schema(
    operation_summary="[Admin] Modifier une question non encore utilisée",
    request_body=QUESTION_MODIFICATION_INPUT,
    responses={
        200: enveloppe('question', QUESTION_ADMIN),
        400: ERREUR,
        403: ERREUR,
        404: ERREUR,
        409: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_supprimer_question_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer une question non encore utilisée",
    responses={
        200: enveloppe('question', NULL_OBJECT),
        403: ERREUR,
        404: ERREUR,
        409: ERREUR,
        500: ERREUR,
    },
    tags=['Formation - Admin'],
)
