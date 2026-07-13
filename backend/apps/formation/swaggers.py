from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


UUID = openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID)
DATE_TIME = openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True)


def enveloppe(nom, schema, avec_message=True):
    props = {'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)}
    if avec_message:
        props['message'] = openapi.Schema(type=openapi.TYPE_STRING)
    props[nom] = schema
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=props)


ERREUR = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'erreur': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

CHOIX_PUBLIC = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={'id': UUID, 'texte': openapi.Schema(type=openapi.TYPE_STRING)},
)

REPONSE_ENREGISTREE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
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
        'module_id': UUID,
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'correction_automatique': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'tentative_id': UUID,
        'statut_tentative': openapi.Schema(type=openapi.TYPE_STRING, enum=['en_cours', 'soumise']),
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
            type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)
        ),
        'sensible_a_la_casse': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

QUESTION_INPUT = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['texte', 'type_question'],
    properties={
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
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['texte'],
                properties={
                    'texte': openapi.Schema(type=openapi.TYPE_STRING),
                    'est_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'explication': openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            description="Requis pour choix_unique et choix_multiple.",
        ),
        'reponses_acceptees': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description="Requis pour reponse_courte.",
        ),
        'sensible_a_la_casse': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

QUIZ_ADMIN = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'module_id': UUID,
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'correction_automatique': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'nombre_questions_banque': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_total_banque': openapi.Schema(type=openapi.TYPE_INTEGER),
        'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_ADMIN),
    },
)

ILLUSTRATION = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'legende': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'image': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    },
)

MODULE_LISTE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'slug': openapi.Schema(type=openapi.TYPE_STRING),
        'resume': openapi.Schema(type=openapi.TYPE_STRING),
        'niveau': openapi.Schema(type=openapi.TYPE_STRING),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'image_couverture': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'date_debut': DATE_TIME,
        'date_fin': DATE_TIME,
        'est_accessible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_lu': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_termine': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

MODULE_DETAIL = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        **MODULE_LISTE.properties,
        'contenu': openapi.Schema(type=openapi.TYPE_STRING),
        'video': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'illustrations': openapi.Schema(type=openapi.TYPE_ARRAY, items=ILLUSTRATION),
        'lu_le': DATE_TIME,
        'quiz_disponible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

MODULE_ADMIN = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        **MODULE_DETAIL.properties,
        'est_publie': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_ouvert': openapi.Schema(type=openapi.TYPE_BOOLEAN),
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
    },
)

TENTATIVE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': UUID,
        'quiz_id': UUID,
        'module_id': UUID,
        'statut': openapi.Schema(type=openapi.TYPE_STRING, enum=['en_cours', 'soumise']),
        'score': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_obtenus': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_total': openapi.Schema(type=openapi.TYPE_INTEGER),
        'est_reussi': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nombre_reponses': openapi.Schema(type=openapi.TYPE_INTEGER),
        'cree_le': DATE_TIME,
        'soumise_le': DATE_TIME,
        'reponses': openapi.Schema(type=openapi.TYPE_ARRAY, items=REPONSE_DETAIL),
    },
)

PARTICIPANT = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'utilisateur_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_nom': openapi.Schema(type=openapi.TYPE_STRING),
        'utilisateur_email': openapi.Schema(type=openapi.TYPE_STRING),
        'est_lu': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'lu_le': DATE_TIME,
        'est_termine': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'termine_le': DATE_TIME,
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
        'terminee_le': DATE_TIME,
    },
)


# =============================================================================
# Ambassadeur
# =============================================================================

swagger_liste_modules_ambassadeur = swagger_auto_schema(
    operation_summary="Lister les modules publiés",
    manual_parameters=[
        openapi.Parameter('niveau', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
    ],
    responses={
        200: enveloppe('modules', openapi.Schema(type=openapi.TYPE_ARRAY, items=MODULE_LISTE), False),
        401: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_detail_module_ambassadeur = swagger_auto_schema(
    operation_summary="Lire un module et débloquer son quiz",
    responses={200: enveloppe('module', MODULE_DETAIL, False), 403: ERREUR, 404: ERREUR},
    tags=['Formation - Ambassadeur'],
)

swagger_quiz_module_ambassadeur = swagger_auto_schema(
    operation_summary="Récupérer ou reprendre une tentative de quiz",
    operation_description=(
        "Crée une tentative si aucune tentative en cours n'existe. Les questions sont tirées "
        "aléatoirement dans la banque puis le tirage est persisté. Les bonnes réponses, les "
        "indicateurs est_correct et les réponses courtes attendues ne sont jamais exposés."
    ),
    responses={200: enveloppe('quiz', QUIZ_PUBLIC), 400: ERREUR, 403: ERREUR, 404: ERREUR},
    tags=['Formation - Ambassadeur'],
)

swagger_repondre_question = swagger_auto_schema(
    operation_summary="Enregistrer la réponse d'une question",
    operation_description=(
        "La réponse est créée ou remplacée pour la question de cette tentative. Si "
        "correction_automatique est désactivée, la réponse ne contient aucun résultat de correction. "
        "Si elle est activée, est_correcte est retourné et, uniquement en cas d'erreur, la bonne "
        "réponse ainsi que l'explication disponible sont ajoutées."
    ),
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
        200: enveloppe(
            'reponse',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': UUID,
                    'question_id': UUID,
                    'enregistree': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'modifiee_le': DATE_TIME,
                    'est_correcte': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'correction': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'explication': openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
        400: ERREUR,
        404: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_soumettre_tentative = swagger_auto_schema(
    operation_summary="Soumettre et noter une tentative",
    operation_description=(
        "Vérifie que toutes les questions tirées ont une réponse, recalcule le score côté serveur, "
        "termine la progression et attribue les points une seule fois en cas de réussite."
    ),
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
    responses={200: enveloppe('tentative', TENTATIVE), 400: ERREUR, 404: ERREUR},
    tags=['Formation - Ambassadeur'],
)

swagger_historique_tentatives = swagger_auto_schema(
    operation_summary="Historique des tentatives du module",
    responses={
        200: enveloppe('tentatives', openapi.Schema(type=openapi.TYPE_ARRAY, items=TENTATIVE), False),
        404: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)

swagger_classement_module = swagger_auto_schema(
    operation_summary="Classement du module",
    responses={
        200: enveloppe('classement', openapi.Schema(type=openapi.TYPE_ARRAY, items=CLASSEMENT), False),
        404: ERREUR,
    },
    tags=['Formation - Ambassadeur'],
)


# =============================================================================
# Admin - modules
# =============================================================================

swagger_liste_modules_admin = swagger_auto_schema(
    operation_summary="[Admin] Lister tous les modules",
    manual_parameters=[
        openapi.Parameter('niveau', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('est_publie', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False),
    ],
    responses={200: enveloppe('modules', openapi.Schema(type=openapi.TYPE_ARRAY, items=MODULE_ADMIN), False)},
    tags=['Formation - Admin'],
)

def _module_form_parameters(champs_requis):
    return [
        openapi.Parameter('titre', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('contenu', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('resume', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('niveau', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('ordre', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('est_publie', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('est_ouvert', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter(
            'date_debut', openapi.IN_FORM, type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME, required=False,
        ),
        openapi.Parameter(
            'date_fin', openapi.IN_FORM, type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME, required=False,
        ),
        openapi.Parameter('video', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
        openapi.Parameter('image_couverture', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
        openapi.Parameter(
            'supprimer_video', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False,
            description="Uniquement en modification : supprime le fichier vidéo actuel.",
        ),
        openapi.Parameter(
            'supprimer_image_couverture', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False,
            description="Uniquement en modification : supprime la couverture actuelle.",
        ),
    ]

swagger_creer_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Créer un module",
    manual_parameters=_module_form_parameters(True),
    consumes=['multipart/form-data'],
    responses={201: enveloppe('module', MODULE_ADMIN), 400: ERREUR},
    tags=['Formation - Admin'],
)

swagger_modifier_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Modifier un module",
    manual_parameters=_module_form_parameters(False),
    consumes=['multipart/form-data'],
    responses={200: enveloppe('module', MODULE_ADMIN), 400: ERREUR, 404: ERREUR},
    tags=['Formation - Admin'],
)

swagger_supprimer_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer un module",
    responses={200: enveloppe('module', openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)), 404: ERREUR},
    tags=['Formation - Admin'],
)

swagger_ouvrir_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Ouvrir un module",
    responses={200: enveloppe('module', MODULE_ADMIN), 404: ERREUR},
    tags=['Formation - Admin'],
)

swagger_fermer_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Fermer un module",
    responses={200: enveloppe('module', MODULE_ADMIN), 404: ERREUR},
    tags=['Formation - Admin'],
)

swagger_participants_module_admin = swagger_auto_schema(
    operation_summary="[Admin] Participants d'un module",
    responses={
        200: enveloppe('participants', openapi.Schema(type=openapi.TYPE_ARRAY, items=PARTICIPANT), False),
        404: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_ajouter_illustration_admin = swagger_auto_schema(
    operation_summary="[Admin] Ajouter une illustration",
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True),
        openapi.Parameter('legende', openapi.IN_FORM, type=openapi.TYPE_STRING),
        openapi.Parameter('ordre', openapi.IN_FORM, type=openapi.TYPE_INTEGER),
    ],
    consumes=['multipart/form-data'],
    responses={201: enveloppe('illustration', ILLUSTRATION), 400: ERREUR, 404: ERREUR},
    tags=['Formation - Admin'],
)

swagger_supprimer_illustration_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer une illustration",
    responses={200: enveloppe('illustration', openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)), 404: ERREUR},
    tags=['Formation - Admin'],
)


# =============================================================================
# Admin - quiz / banque
# =============================================================================

swagger_creer_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Créer le quiz unique d'un module",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['titre', 'nombre_questions'],
        properties={
            'titre': openapi.Schema(type=openapi.TYPE_STRING),
            'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER, default=50),
            'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER, default=5),
            'correction_automatique': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
            'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_INPUT),
        },
    ),
    responses={201: enveloppe('quiz', QUIZ_ADMIN), 400: ERREUR, 404: ERREUR},
    tags=['Formation - Admin'],
)

swagger_detail_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Consulter un quiz et sa banque",
    responses={200: enveloppe('quiz', QUIZ_ADMIN, False), 404: ERREUR},
    tags=['Formation - Admin'],
)

swagger_modifier_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Modifier les paramètres d'un quiz",
    operation_description=(
        "Les questions peuvent être remplacées uniquement tant qu'aucune tentative n'existe. "
        "Pour une banque déjà utilisée, ajoutez de nouvelles questions avec l'endpoint dédié."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'titre': openapi.Schema(type=openapi.TYPE_STRING),
            'score_de_reussite': openapi.Schema(type=openapi.TYPE_INTEGER),
            'nombre_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
            'correction_automatique': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_INPUT),
        },
    ),
    responses={200: enveloppe('quiz', QUIZ_ADMIN), 400: ERREUR, 404: ERREUR, 409: ERREUR},
    tags=['Formation - Admin'],
)

swagger_supprimer_quiz_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer un quiz",
    responses={200: enveloppe('quiz', openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)), 404: ERREUR},
    tags=['Formation - Admin'],
)

swagger_ajouter_questions_banque_admin = swagger_auto_schema(
    operation_summary="[Admin] Ajouter des questions à la banque",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['questions'],
        properties={
            'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_INPUT),
        },
    ),
    responses={
        201: enveloppe('questions', openapi.Schema(type=openapi.TYPE_ARRAY, items=QUESTION_ADMIN)),
        400: ERREUR,
        404: ERREUR,
    },
    tags=['Formation - Admin'],
)

swagger_modifier_question_admin = swagger_auto_schema(
    operation_summary="[Admin] Modifier une question non encore utilisée",
    request_body=QUESTION_INPUT,
    responses={200: enveloppe('question', QUESTION_ADMIN), 400: ERREUR, 404: ERREUR, 409: ERREUR},
    tags=['Formation - Admin'],
)

swagger_supprimer_question_admin = swagger_auto_schema(
    operation_summary="[Admin] Supprimer une question non encore utilisée",
    responses={200: enveloppe('question', openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)), 404: ERREUR, 409: ERREUR},
    tags=['Formation - Admin'],
)
