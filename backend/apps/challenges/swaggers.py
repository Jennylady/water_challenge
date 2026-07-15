from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


NIVEAUX = ['debutant', 'apprenti', 'actif', 'leader']
STATUTS_DEFI = ['verrouille', 'disponible', 'en_cours', 'termine']
STATUTS_SOUMISSION = ['en_attente', 'validee', 'refusee']
DECISIONS_VALIDATION = ['acceptee', 'refusee']


def enveloppe(nom_attribut, schema_valeur, avec_message=True):
    properties = {'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)}
    if avec_message:
        properties['message'] = openapi.Schema(type=openapi.TYPE_STRING)
    properties[nom_attribut] = schema_valeur
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=properties)


def schema_liste(items):
    return openapi.Schema(type=openapi.TYPE_ARRAY, items=items)


def schema_nullable(type_, **kwargs):
    return openapi.Schema(type=type_, x_nullable=True, **kwargs)


ERREUR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['success', 'erreur'],
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'erreur': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

REPONSE_NULLE_SCHEMA = schema_nullable(openapi.TYPE_OBJECT)

PHOTO_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'image_url': schema_nullable(openapi.TYPE_STRING),
        'ajoutee_le': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
    },
)

VALIDATION_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'decision': openapi.Schema(
            type=openapi.TYPE_STRING, enum=DECISIONS_VALIDATION
        ),
        'commentaire': schema_nullable(openapi.TYPE_STRING),
        'points_attribues': openapi.Schema(type=openapi.TYPE_INTEGER),
        'validateur_id': schema_nullable(openapi.TYPE_INTEGER),
        'validateur_nom': schema_nullable(openapi.TYPE_STRING),
        'valide_le': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
    },
)

SOUMISSION_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'defi_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'defi_titre': openapi.Schema(type=openapi.TYPE_STRING),
        'utilisateur_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_nom': openapi.Schema(type=openapi.TYPE_STRING),
        'utilisateur_email': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
        ),
        'rapport': openapi.Schema(type=openapi.TYPE_STRING),
        'date_activite': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
        ),
        'lieu': openapi.Schema(type=openapi.TYPE_STRING),
        'nombre_personnes_sensibilisees': openapi.Schema(
            type=openapi.TYPE_INTEGER
        ),
        'video_url': schema_nullable(openapi.TYPE_STRING),
        'photos': schema_liste(PHOTO_SCHEMA),
        'statut': openapi.Schema(
            type=openapi.TYPE_STRING, enum=STATUTS_SOUMISSION
        ),
        'validation': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            x_nullable=True,
            properties=VALIDATION_SCHEMA.properties,
        ),
        'soumis_le': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
        'modifie_le': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
        'traitee_le': schema_nullable(
            openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
    },
)

DEFI_LISTE_PROPERTIES = {
    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
    'module_slug': schema_nullable(openapi.TYPE_STRING),
    'module_titre': schema_nullable(openapi.TYPE_STRING),
    'titre': openapi.Schema(type=openapi.TYPE_STRING),
    'description': openapi.Schema(type=openapi.TYPE_STRING),
    'image_couverture_url': schema_nullable(openapi.TYPE_STRING),
    'niveau': openapi.Schema(type=openapi.TYPE_STRING, enum=NIVEAUX),
    'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
    'duree_estimee': openapi.Schema(type=openapi.TYPE_STRING),
    'points_recompense': openapi.Schema(type=openapi.TYPE_INTEGER),
    'nombre_photos_min': openapi.Schema(type=openapi.TYPE_INTEGER),
    'nombre_photos_max': openapi.Schema(type=openapi.TYPE_INTEGER),
    'video_obligatoire': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'est_obligatoire': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'est_accessible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'statut': openapi.Schema(type=openapi.TYPE_STRING, enum=STATUTS_DEFI),
    'debloque_le': schema_nullable(
        openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
    ),
    'commence_le': schema_nullable(
        openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
    ),
    'termine_le': schema_nullable(
        openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
    ),
    'a_soumission_en_attente': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'date_debut': schema_nullable(
        openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
    ),
    'date_fin': schema_nullable(
        openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
    ),
}

DEFI_LISTE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT, properties=DEFI_LISTE_PROPERTIES
)

DEFI_DETAIL_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        **DEFI_LISTE_PROPERTIES,
        'resultat_attendu': openapi.Schema(type=openapi.TYPE_STRING),
        'criteres_validation': openapi.Schema(type=openapi.TYPE_STRING),
        'derniere_soumission': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            x_nullable=True,
            properties=SOUMISSION_SCHEMA.properties,
        ),
    },
)

DEFI_ADMIN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'module_slug': schema_nullable(openapi.TYPE_STRING),
        'module_titre': schema_nullable(openapi.TYPE_STRING),
        'titre': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'resultat_attendu': openapi.Schema(type=openapi.TYPE_STRING),
        'criteres_validation': openapi.Schema(type=openapi.TYPE_STRING),
        'image_couverture_url': schema_nullable(openapi.TYPE_STRING),
        'niveau': openapi.Schema(type=openapi.TYPE_STRING, enum=NIVEAUX),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'duree_estimee': openapi.Schema(type=openapi.TYPE_STRING),
        'points_recompense': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nombre_photos_min': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nombre_photos_max': openapi.Schema(type=openapi.TYPE_INTEGER),
        'video_obligatoire': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_obligatoire': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_actif': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_publie': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'est_ouvert': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'date_debut': schema_nullable(
            openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
        'date_fin': schema_nullable(
            openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
        'est_accessible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'nb_participants': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nb_termines': openapi.Schema(type=openapi.TYPE_INTEGER),
        'nb_soumissions_en_attente': openapi.Schema(type=openapi.TYPE_INTEGER),
        'cree_le': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
        'modifie_le': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
    },
)

PARTICIPANT_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'utilisateur_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_nom': openapi.Schema(type=openapi.TYPE_STRING),
        'utilisateur_email': openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
        ),
        'statut': openapi.Schema(type=openapi.TYPE_STRING, enum=STATUTS_DEFI),
        'debloque_le': schema_nullable(
            openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
        'commence_le': schema_nullable(
            openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
        'termine_le': schema_nullable(
            openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
        'nb_soumissions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'derniere_soumission_statut': schema_nullable(openapi.TYPE_STRING),
    },
)

STATISTIQUES_UTILISATEUR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'defis_verrouilles': openapi.Schema(type=openapi.TYPE_INTEGER),
        'defis_disponibles': openapi.Schema(type=openapi.TYPE_INTEGER),
        'defis_en_cours': openapi.Schema(type=openapi.TYPE_INTEGER),
        'defis_termines': openapi.Schema(type=openapi.TYPE_INTEGER),
        'soumissions_en_attente': openapi.Schema(type=openapi.TYPE_INTEGER),
        'soumissions_validees': openapi.Schema(type=openapi.TYPE_INTEGER),
        'soumissions_refusees': openapi.Schema(type=openapi.TYPE_INTEGER),
        'personnes_sensibilisees': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points': openapi.Schema(type=openapi.TYPE_INTEGER),
        'niveau': schema_nullable(openapi.TYPE_STRING),
        'progression': openapi.Schema(type=openapi.TYPE_INTEGER),
        'badge_courant': schema_nullable(openapi.TYPE_STRING),
    },
)

STATISTIQUES_ADMIN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'defis_total': openapi.Schema(type=openapi.TYPE_INTEGER),
        'defis_actifs': openapi.Schema(type=openapi.TYPE_INTEGER),
        'participants_uniques': openapi.Schema(type=openapi.TYPE_INTEGER),
        'defis_termines': openapi.Schema(type=openapi.TYPE_INTEGER),
        'soumissions_total': openapi.Schema(type=openapi.TYPE_INTEGER),
        'soumissions_en_attente': openapi.Schema(type=openapi.TYPE_INTEGER),
        'soumissions_validees': openapi.Schema(type=openapi.TYPE_INTEGER),
        'soumissions_refusees': openapi.Schema(type=openapi.TYPE_INTEGER),
        'personnes_sensibilisees': openapi.Schema(type=openapi.TYPE_INTEGER),
        'points_attribues': openapi.Schema(type=openapi.TYPE_INTEGER),
    },
)


# =============================================================================
# AMBASSADEUR
# =============================================================================

swagger_liste_defis = swagger_auto_schema(
    operation_summary='Lister les défis avec le statut personnel',
    operation_description=(
        "Les défis accessibles sont synchronisés selon leur publication, leur période "
        "d'ouverture et le niveau de l'utilisateur. La lecture du module et le quiz ne "
        "conditionnent pas leur disponibilité."
    ),
    manual_parameters=[
        openapi.Parameter(
            'niveau', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False, enum=NIVEAUX,
        ),
        openapi.Parameter(
            'statut', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False, enum=STATUTS_DEFI,
        ),
        openapi.Parameter(
            'module_slug', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False,
        ),
        openapi.Parameter(
            'est_obligatoire', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
            required=False,
        ),
    ],
    responses={
        200: enveloppe('defis', schema_liste(DEFI_LISTE_SCHEMA), avec_message=False),
        400: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_detail_defi = swagger_auto_schema(
    operation_summary="Consulter le détail d'un défi",
    responses={
        200: enveloppe('defi', DEFI_DETAIL_SCHEMA, avec_message=False),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_commencer_defi = swagger_auto_schema(
    operation_summary='Commencer un défi disponible',
    operation_description=(
        "Passe le suivi du défi de 'disponible' à 'en_cours'. Aucun quiz préalable "
        "n'est requis."
    ),
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
    responses={
        200: enveloppe('defi', DEFI_DETAIL_SCHEMA),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_soumettre_activite = swagger_auto_schema(
    operation_summary="Envoyer les preuves d'une activité",
    operation_description=(
        "Requête multipart. Répéter la clé 'photos' pour plusieurs images. Le nombre "
        "de photos et l'obligation d'une vidéo dépendent de la configuration du défi."
    ),
    manual_parameters=[
        openapi.Parameter(
            'rapport', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True
        ),
        openapi.Parameter(
            'date_activite', openapi.IN_FORM, type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE, required=True,
        ),
        openapi.Parameter(
            'lieu', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True
        ),
        openapi.Parameter(
            'nombre_personnes_sensibilisees', openapi.IN_FORM,
            type=openapi.TYPE_INTEGER, required=False, default=0,
        ),
        openapi.Parameter(
            'photos', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True,
            description='Répéter cette clé pour envoyer plusieurs photos.',
        ),
        openapi.Parameter(
            'video', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False
        ),
    ],
    consumes=['multipart/form-data'],
    responses={
        201: enveloppe('soumission', SOUMISSION_SCHEMA),
        400: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_mes_soumissions = swagger_auto_schema(
    operation_summary="Lister l'historique de mes activités",
    manual_parameters=[
        openapi.Parameter(
            'statut', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False, enum=STATUTS_SOUMISSION,
        ),
        openapi.Parameter(
            'defi_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
            required=False,
        ),
    ],
    responses={
        200: enveloppe(
            'soumissions', schema_liste(SOUMISSION_SCHEMA), avec_message=False
        ),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_detail_soumission = swagger_auto_schema(
    operation_summary='Consulter une de mes soumissions',
    responses={
        200: enveloppe('soumission', SOUMISSION_SCHEMA, avec_message=False),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_annuler_soumission = swagger_auto_schema(
    operation_summary='Annuler une soumission encore en attente',
    responses={
        200: enveloppe('soumission', REPONSE_NULLE_SCHEMA),
        400: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_mes_statistiques = swagger_auto_schema(
    operation_summary="Consulter mes statistiques de défis et d'impact",
    responses={
        200: enveloppe(
            'statistiques', STATISTIQUES_UTILISATEUR_SCHEMA,
            avec_message=False,
        ),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)


# =============================================================================
# ADMIN - DÉFIS
# =============================================================================

swagger_admin_liste_defis = swagger_auto_schema(
    operation_summary='[Admin] Lister tous les défis',
    manual_parameters=[
        openapi.Parameter(
            'niveau', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False, enum=NIVEAUX,
        ),
        openapi.Parameter(
            'est_publie', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
            required=False,
        ),
        openapi.Parameter(
            'est_actif', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
            required=False,
        ),
        openapi.Parameter(
            'module_slug', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False,
        ),
    ],
    responses={
        200: enveloppe('defis', schema_liste(DEFI_ADMIN_SCHEMA), avec_message=False),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)


def _defi_form_parameters(champs_requis):
    return [
        openapi.Parameter(
            'module_slug', openapi.IN_FORM, type=openapi.TYPE_STRING,
            required=False,
            description=(
                "Slug du module associé. Lors d'une modification, envoyer une valeur "
                "vide pour détacher le défi du module."
            ),
        ),
        openapi.Parameter(
            'titre', openapi.IN_FORM, type=openapi.TYPE_STRING,
            required=champs_requis,
        ),
        openapi.Parameter(
            'description', openapi.IN_FORM, type=openapi.TYPE_STRING,
            required=champs_requis,
        ),
        openapi.Parameter(
            'resultat_attendu', openapi.IN_FORM, type=openapi.TYPE_STRING,
            required=champs_requis,
        ),
        openapi.Parameter(
            'criteres_validation', openapi.IN_FORM, type=openapi.TYPE_STRING,
            required=champs_requis,
        ),
        openapi.Parameter(
            'image_couverture', openapi.IN_FORM, type=openapi.TYPE_FILE,
            required=False,
        ),
        openapi.Parameter(
            'niveau', openapi.IN_FORM, type=openapi.TYPE_STRING,
            required=champs_requis, enum=NIVEAUX,
        ),
        openapi.Parameter(
            'ordre', openapi.IN_FORM, type=openapi.TYPE_INTEGER,
            required=False, default=0,
        ),
        openapi.Parameter(
            'duree_estimee', openapi.IN_FORM, type=openapi.TYPE_STRING,
            required=champs_requis,
        ),
        openapi.Parameter(
            'points_recompense', openapi.IN_FORM, type=openapi.TYPE_INTEGER,
            required=False, default=10,
        ),
        openapi.Parameter(
            'nombre_photos_min', openapi.IN_FORM, type=openapi.TYPE_INTEGER,
            required=False, default=1,
        ),
        openapi.Parameter(
            'nombre_photos_max', openapi.IN_FORM, type=openapi.TYPE_INTEGER,
            required=False, default=5,
        ),
        openapi.Parameter(
            'video_obligatoire', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN,
            required=False, default=False,
        ),
        openapi.Parameter(
            'est_obligatoire', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN,
            required=False, default=True,
        ),
        openapi.Parameter(
            'est_actif', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN,
            required=False, default=True,
        ),
        openapi.Parameter(
            'est_publie', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN,
            required=False, default=True,
        ),
        openapi.Parameter(
            'est_ouvert', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN,
            required=False, default=True,
        ),
        openapi.Parameter(
            'date_debut', openapi.IN_FORM, type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME, required=False,
        ),
        openapi.Parameter(
            'date_fin', openapi.IN_FORM, type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME, required=False,
        ),
    ]


swagger_creer_defi = swagger_auto_schema(
    operation_summary='[Admin] Créer un défi',
    manual_parameters=_defi_form_parameters(True),
    consumes=['multipart/form-data'],
    responses={
        201: enveloppe('defi', DEFI_ADMIN_SCHEMA),
        400: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_modifier_defi = swagger_auto_schema(
    operation_summary='[Admin] Modifier un défi',
    manual_parameters=_defi_form_parameters(False),
    consumes=['multipart/form-data'],
    responses={
        200: enveloppe('defi', DEFI_ADMIN_SCHEMA),
        400: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_supprimer_defi = swagger_auto_schema(
    operation_summary='[Admin] Supprimer un défi',
    responses={
        200: enveloppe('defi', REPONSE_NULLE_SCHEMA),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_ouvrir_defi = swagger_auto_schema(
    operation_summary='[Admin] Ouvrir manuellement un défi',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
    responses={
        200: enveloppe('defi', DEFI_ADMIN_SCHEMA),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_fermer_defi = swagger_auto_schema(
    operation_summary='[Admin] Fermer manuellement un défi',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
    responses={
        200: enveloppe('defi', DEFI_ADMIN_SCHEMA),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_participants_defi = swagger_auto_schema(
    operation_summary="[Admin/Validateur] Lister les participants d'un défi",
    manual_parameters=[
        openapi.Parameter(
            'statut', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False, enum=STATUTS_DEFI,
        ),
    ],
    responses={
        200: enveloppe(
            'participants', schema_liste(PARTICIPANT_SCHEMA),
            avec_message=False,
        ),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)


# =============================================================================
# ADMIN / VALIDATEUR - SOUMISSIONS
# =============================================================================

swagger_admin_liste_soumissions = swagger_auto_schema(
    operation_summary='[Admin/Validateur] Lister les soumissions',
    manual_parameters=[
        openapi.Parameter(
            'statut', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False, enum=STATUTS_SOUMISSION,
        ),
        openapi.Parameter(
            'defi_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
            required=False,
        ),
        openapi.Parameter(
            'utilisateur_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
            required=False,
        ),
        openapi.Parameter(
            'recherche', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            required=False,
        ),
    ],
    responses={
        200: enveloppe(
            'soumissions', schema_liste(SOUMISSION_SCHEMA),
            avec_message=False,
        ),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)

swagger_admin_detail_soumission = swagger_auto_schema(
    operation_summary=(
        "[Admin/Validateur] Consulter toutes les preuves d'une soumission"
    ),
    responses={
        200: enveloppe('soumission', SOUMISSION_SCHEMA, avec_message=False),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)

swagger_valider_soumission = swagger_auto_schema(
    operation_summary='[Admin/Validateur] Accepter ou refuser une soumission',
    operation_description=(
        "L'acceptation termine le défi et attribue les points une seule fois. Le "
        "commentaire est obligatoire en cas de refus."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['decision'],
        properties={
            'decision': openapi.Schema(
                type=openapi.TYPE_STRING, enum=DECISIONS_VALIDATION
            ),
            'commentaire': openapi.Schema(type=openapi.TYPE_STRING),
            'points_attribues': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                minimum=0,
                description=(
                    'Facultatif. Par défaut, utilise points_recompense du défi.'
                ),
            ),
        },
    ),
    responses={
        200: enveloppe('soumission', SOUMISSION_SCHEMA),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        409: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)

swagger_admin_statistiques = swagger_auto_schema(
    operation_summary=(
        '[Admin/Validateur] Statistiques globales des défis et de l\'impact'
    ),
    responses={
        200: enveloppe(
            'statistiques', STATISTIQUES_ADMIN_SCHEMA, avec_message=False
        ),
        401: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        500: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)
