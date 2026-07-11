from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# ---------------------------------------------------------------------------
# Schémas réutilisables (doivent correspondre EXACTEMENT à ce que renvoient
# les serializers / views correspondants). Enveloppe uniforme :
# {"success": bool, "message"|"erreur": str, "<nom_attribut>": objet|liste}
# ---------------------------------------------------------------------------

def enveloppe(nom_attribut, schema_valeur, avec_message=True):
    properties = {'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)}
    if avec_message:
        properties['message'] = openapi.Schema(type=openapi.TYPE_STRING)
    properties[nom_attribut] = schema_valeur
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=properties)


ERREUR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'erreur': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

CHOIX_AMBASSADEUR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

QUESTION_AMBASSADEUR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
        'type_question': openapi.Schema(
            type=openapi.TYPE_STRING, enum=['choix_unique', 'choix_multiple', 'reponse_courte']
        ),
        'points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'choix': openapi.Schema(type=openapi.TYPE_ARRAY, items=CHOIX_AMBASSADEUR_SCHEMA),
    },
)

QUIZ_AMBASSADEUR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
        'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_AMBASSADEUR_SCHEMA),
    },
)

CHOIX_ADMIN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
        'est_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'explication': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    },
)

QUESTION_ADMIN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
        'type_question': openapi.Schema(
            type=openapi.TYPE_STRING, enum=['choix_unique', 'choix_multiple', 'reponse_courte']
        ),
        'points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'choix': openapi.Schema(type=openapi.TYPE_ARRAY, items=CHOIX_ADMIN_SCHEMA),
        'reponses_acceptees': openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)
        ),
        'sensible_a_la_casse': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

QUIZ_ADMIN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'module_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_total': openapi.Schema(type=openapi.TYPE_INTEGER),
        'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_ADMIN_SCHEMA),
    },
)

ILLUSTRATION_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'legende': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'image_url': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    },
)

MODULE_LISTE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'slug': openapi.Schema(type=openapi.TYPE_STRING),
        'resume': openapi.Schema(type=openapi.TYPE_STRING),
        'niveau': openapi.Schema(type=openapi.TYPE_STRING),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'image_couverture_url': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'date_debut': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'date_fin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'est_accessible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_lu': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_termine': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

MODULE_DETAIL_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'slug': openapi.Schema(type=openapi.TYPE_STRING),
        'contenu': openapi.Schema(type=openapi.TYPE_STRING),
        'resume': openapi.Schema(type=openapi.TYPE_STRING),
        'niveau': openapi.Schema(type=openapi.TYPE_STRING),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'url_video': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'image_couverture_url': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'illustrations': openapi.Schema(type=openapi.TYPE_ARRAY, items=ILLUSTRATION_SCHEMA),
        'date_debut': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'date_fin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'est_accessible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_lu': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'lu_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'est_termine': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'quiz_disponible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

MODULE_ADMIN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'slug': openapi.Schema(type=openapi.TYPE_STRING),
        'contenu': openapi.Schema(type=openapi.TYPE_STRING),
        'resume': openapi.Schema(type=openapi.TYPE_STRING),
        'niveau': openapi.Schema(type=openapi.TYPE_STRING),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'est_publie': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_ouvert': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'date_debut': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'date_fin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'est_accessible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'url_video': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'image_couverture_url': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'illustrations': openapi.Schema(type=openapi.TYPE_ARRAY, items=ILLUSTRATION_SCHEMA),
        'a_un_quiz': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'nb_participants': openapi.Schema(type=openapi.TYPE_INTEGER),
        'cree_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'modifie_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    },
)

PARTICIPANT_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'utilisateur_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_nom': openapi.Schema(type=openapi.TYPE_STRING),
        'utilisateur_email': openapi.Schema(type=openapi.TYPE_STRING),
        'est_lu': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'lu_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'est_termine': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'termine_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
    },
)

CLASSEMENT_ENTREE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rang': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_nom': openapi.Schema(type=openapi.TYPE_STRING),
        'meilleur_score': openapi.Schema(type=openapi.TYPE_INTEGER),
        'meilleurs_points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'est_reussi': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'tentatives_effectuees': openapi.Schema(type=openapi.TYPE_INTEGER),
        'terminee_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
    },
)

REPONSE_TENTATIVE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'question_texte': openapi.Schema(type=openapi.TYPE_STRING),
        'type_question': openapi.Schema(type=openapi.TYPE_STRING),
        'choix_selectionnes': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'texte': openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
        'reponse_texte': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'est_correcte': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'points_obtenus': openapi.Schema(type=openapi.TYPE_INTEGER),
    },
)

TENTATIVE_QUIZ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'quiz_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'module_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'score': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_obtenus': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_total': openapi.Schema(type=openapi.TYPE_INTEGER),
        'est_reussi': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'cree_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'reponses': openapi.Schema(type=openapi.TYPE_ARRAY, items=REPONSE_TENTATIVE_SCHEMA),
    },
)


# ---------------------------------------------------------------------------
# AMBASSADEUR
# ---------------------------------------------------------------------------

swagger_liste_modules_ambassadeur = swagger_auto_schema(
    operation_summary="Lister les modules de formation publiés",
    operation_description="Retourne la liste des modules publiés avec la progression de l'utilisateur connecté.",
    manual_parameters=[
        openapi.Parameter('niveau', openapi.IN_QUERY, description="Filtrer par niveau", type=openapi.TYPE_STRING, required=False),
    ],
    responses={
        200: enveloppe('modules', openapi.Schema(type=openapi.TYPE_ARRAY, items=MODULE_LISTE_SCHEMA), avec_message=False),
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_detail_module_ambassadeur = swagger_auto_schema(
    operation_summary="Consulter un module (marque la lecture et débloque le quiz)",
    operation_description="Retourne le détail d'un module. Marque automatiquement le module comme lu, ce qui débloque le quiz.",
    responses={
        200: enveloppe('module', MODULE_DETAIL_SCHEMA, avec_message=False),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_quiz_module_ambassadeur = swagger_auto_schema(
    operation_summary="Récupérer le quiz d'un module (sans les bonnes réponses)",
    operation_description="Accessible uniquement si le module a déjà été lu et si le module est ouvert.",
    responses={
        200: enveloppe('quiz', QUIZ_AMBASSADEUR_SCHEMA, avec_message=False),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_soumettre_quiz = swagger_auto_schema(
    operation_summary="Soumettre les réponses à un quiz (scoring automatique)",
    operation_description=(
        "Calcule automatiquement le score (avec points par question), enregistre la tentative "
        "et met à jour la progression du module. Supporte choix_unique, choix_multiple et reponse_courte."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['reponses'],
        properties={
            'reponses': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['question_id'],
                    properties={
                        'question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'choix_ids': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_INTEGER),
                            description="Pour choix_unique (1 élément) ou choix_multiple (N éléments)",
                        ),
                        'reponse_texte': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Pour les questions de type reponse_courte",
                        ),
                    },
                ),
            ),
        },
    ),
    responses={
        201: enveloppe('tentative', TENTATIVE_QUIZ_SCHEMA),
        400: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_historique_tentatives = swagger_auto_schema(
    operation_summary="Historique des tentatives de quiz d'un module pour l'utilisateur connecté",
    responses={
        200: enveloppe('tentatives', openapi.Schema(type=openapi.TYPE_ARRAY, items=TENTATIVE_QUIZ_SCHEMA), avec_message=False),
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_classement_module = swagger_auto_schema(
    operation_summary="Classement (leaderboard) des participants d'un module",
    responses={
        200: enveloppe('classement', openapi.Schema(type=openapi.TYPE_ARRAY, items=CLASSEMENT_ENTREE_SCHEMA), avec_message=False),
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Ambassadeur'],
)


# ---------------------------------------------------------------------------
# ADMIN - Modules
# ---------------------------------------------------------------------------

swagger_liste_modules_admin = swagger_auto_schema(
    operation_summary="[Admin] Lister tous les modules (publiés ou non)",
    manual_parameters=[
        openapi.Parameter('niveau', openapi.IN_QUERY, description="Filtrer par niveau", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('est_publie', openapi.IN_QUERY, description="Filtrer par statut de publication", type=openapi.TYPE_BOOLEAN, required=False),
    ],
    responses={
        200: enveloppe('modules', openapi.Schema(type=openapi.TYPE_ARRAY, items=MODULE_ADMIN_SCHEMA), avec_message=False),
        403: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

# Requête multipart => tous les paramètres du body doivent être déclarés en manual_parameters
swagger_creer_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Créer un module de formation",
    manual_parameters=[
        openapi.Parameter('titre', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('contenu', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('resume', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('niveau', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('ordre', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('est_publie', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('est_ouvert', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('date_debut', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, required=False),
        openapi.Parameter('date_fin', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, required=False),
        openapi.Parameter('url_video', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('image_couverture', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
    ],
    consumes=['multipart/form-data'],
    responses={
        201: enveloppe('module', MODULE_ADMIN_SCHEMA),
        400: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_modifier_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Modifier un module de formation",
    manual_parameters=[
        openapi.Parameter('titre', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('contenu', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('resume', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('niveau', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('ordre', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('est_publie', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('est_ouvert', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('date_debut', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, required=False),
        openapi.Parameter('date_fin', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, required=False),
        openapi.Parameter('url_video', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('image_couverture', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
    ],
    consumes=['multipart/form-data'],
    responses={
        200: enveloppe('module', MODULE_ADMIN_SCHEMA),
        400: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_supprimer_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer un module de formation",
    responses={
        200: enveloppe('module', openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_ouvrir_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Ouvrir manuellement un module",
    responses={
        200: enveloppe('module', MODULE_ADMIN_SCHEMA),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_fermer_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Fermer manuellement un module",
    responses={
        200: enveloppe('module', MODULE_ADMIN_SCHEMA),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_participants_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Lister les participants d'un module",
    responses={
        200: enveloppe('participants', openapi.Schema(type=openapi.TYPE_ARRAY, items=PARTICIPANT_SCHEMA), avec_message=False),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_ajouter_illustration_admin = swagger_auto_schema(
    operation_summary="[Admin] Ajouter une illustration à un module",
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True),
        openapi.Parameter('legende', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('ordre', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
    ],
    consumes=['multipart/form-data'],
    responses={
        201: enveloppe('illustration', ILLUSTRATION_SCHEMA),
        400: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_supprimer_illustration_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer une illustration",
    responses={
        200: enveloppe('illustration', openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)


# ---------------------------------------------------------------------------
# ADMIN - Quiz
# ---------------------------------------------------------------------------

CHOIX_INPUT_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['texte', 'est_correct'],
    properties={
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
        'est_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'explication': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

QUESTION_INPUT_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['texte', 'type_question'],
    properties={
        'texte': openapi.Schema(type=openapi.TYPE_STRING),
        'type_question': openapi.Schema(
            type=openapi.TYPE_STRING, enum=['choix_unique', 'choix_multiple', 'reponse_courte']
        ),
        'points': openapi.Schema(type=openapi.TYPE_INTEGER, description="Points attribués (défaut 1)"),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'choix': openapi.Schema(
            type=openapi.TYPE_ARRAY, items=CHOIX_INPUT_SCHEMA,
            description="Requis pour choix_unique / choix_multiple",
        ),
        'reponses_acceptees': openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
            description="Requis pour reponse_courte",
        ),
        'sensible_a_la_casse': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

swagger_creer_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Créer le quiz d'un module (questions + choix imbriqués)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['titre', 'questions'],
        properties={
            'titre': openapi.Schema(type=openapi.TYPE_STRING),
            'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
            'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_INPUT_SCHEMA),
        },
    ),
    responses={
        201: enveloppe('quiz', QUIZ_ADMIN_SCHEMA),
        400: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_detail_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Détail d'un quiz (avec les bonnes réponses)",
    responses={
        200: enveloppe('quiz', QUIZ_ADMIN_SCHEMA, avec_message=False),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_modifier_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Modifier le titre / score de réussite d'un quiz",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'titre': openapi.Schema(type=openapi.TYPE_STRING),
            'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
    ),
    responses={
        200: enveloppe('quiz', QUIZ_ADMIN_SCHEMA),
        400: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)

swagger_supprimer_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer un quiz",
    responses={
        200: enveloppe('quiz', openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Formation - Admin'],
)