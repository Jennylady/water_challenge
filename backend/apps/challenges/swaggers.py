from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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

VALIDATION_PROPERTIES = {
    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
    'decision': openapi.Schema(type=openapi.TYPE_STRING, enum=['acceptee', 'refusee']),
    'commentaire': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    'points_attribues': openapi.Schema(type=openapi.TYPE_INTEGER),
    'validateur_id': openapi.Schema(type=openapi.TYPE_INTEGER, x_nullable=True),
    'validateur_nom': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    'valide_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
}
VALIDATION_SCHEMA = openapi.Schema(type=openapi.TYPE_OBJECT, properties=VALIDATION_PROPERTIES)

PHOTO_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
        'image_url': openapi.Schema(type=openapi.TYPE_STRING),
        'ajoutee_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    },
)

SOUMISSION_PROPERTIES = {
    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
    'defi_id': openapi.Schema(type=openapi.TYPE_INTEGER),
    'defi_titre': openapi.Schema(type=openapi.TYPE_STRING),
    'utilisateur_id': openapi.Schema(type=openapi.TYPE_INTEGER),
    'utilisateur_nom': openapi.Schema(type=openapi.TYPE_STRING),
    'utilisateur_email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
    'rapport': openapi.Schema(type=openapi.TYPE_STRING),
    'date_activite': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
    'lieu': openapi.Schema(type=openapi.TYPE_STRING),
    'nombre_personnes_sensibilisees': openapi.Schema(type=openapi.TYPE_INTEGER),
    'video_url': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    'photos': openapi.Schema(type=openapi.TYPE_ARRAY, items=PHOTO_SCHEMA),
    'statut': openapi.Schema(type=openapi.TYPE_STRING, enum=['en_attente', 'validee', 'refusee']),
    'validation': openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True, properties=VALIDATION_PROPERTIES),
    'soumis_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    'modifie_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    'traitee_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
}
SOUMISSION_SCHEMA = openapi.Schema(type=openapi.TYPE_OBJECT, properties=SOUMISSION_PROPERTIES)

DEFI_PROPERTIES = {
    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
    'module_id': openapi.Schema(type=openapi.TYPE_INTEGER, x_nullable=True),
    'module_titre': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    'titre': openapi.Schema(type=openapi.TYPE_STRING),
    'description': openapi.Schema(type=openapi.TYPE_STRING),
    'resultat_attendu': openapi.Schema(type=openapi.TYPE_STRING),
    'criteres_validation': openapi.Schema(type=openapi.TYPE_STRING),
    'image_couverture_url': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
    'niveau': openapi.Schema(type=openapi.TYPE_STRING, enum=['debutant', 'apprenti', 'actif', 'leader']),
    'ordre': openapi.Schema(type=openapi.TYPE_INTEGER),
    'duree_estimee': openapi.Schema(type=openapi.TYPE_STRING),
    'points_recompense': openapi.Schema(type=openapi.TYPE_INTEGER),
    'nombre_photos_min': openapi.Schema(type=openapi.TYPE_INTEGER),
    'nombre_photos_max': openapi.Schema(type=openapi.TYPE_INTEGER),
    'video_obligatoire': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'est_obligatoire': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'est_accessible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'statut': openapi.Schema(type=openapi.TYPE_STRING, enum=['verrouille', 'disponible', 'en_cours', 'termine']),
    'debloque_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
    'commence_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
    'termine_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
    'a_soumission_en_attente': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'date_debut': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
    'date_fin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
    'derniere_soumission': openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True, properties=SOUMISSION_PROPERTIES),
}
DEFI_SCHEMA = openapi.Schema(type=openapi.TYPE_OBJECT, properties=DEFI_PROPERTIES)

DEFI_ADMIN_PROPERTIES = {
    **DEFI_PROPERTIES,
    'est_actif': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'est_publie': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'est_ouvert': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'nb_participants': openapi.Schema(type=openapi.TYPE_INTEGER),
    'nb_termines': openapi.Schema(type=openapi.TYPE_INTEGER),
    'nb_soumissions_en_attente': openapi.Schema(type=openapi.TYPE_INTEGER),
    'cree_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    'modifie_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
}
DEFI_ADMIN_SCHEMA = openapi.Schema(type=openapi.TYPE_OBJECT, properties=DEFI_ADMIN_PROPERTIES)

PARTICIPANT_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'utilisateur_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'utilisateur_nom': openapi.Schema(type=openapi.TYPE_STRING),
        'utilisateur_email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'statut': openapi.Schema(type=openapi.TYPE_STRING),
        'debloque_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'commence_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'termine_le': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, x_nullable=True),
        'nb_soumissions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'derniere_soumission_statut': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
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
        'niveau': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        'progression': openapi.Schema(type=openapi.TYPE_INTEGER),
        'badge_courant': openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
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
    operation_summary="Lister les défis avec le statut personnel",
    operation_description=(
        "Synchronise automatiquement les défis de l'utilisateur. Un défi lié à un module "
        "devient disponible après réussite du quiz et si le niveau de l'utilisateur l'autorise."
    ),
    manual_parameters=[
        openapi.Parameter('niveau', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('statut', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('module_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('est_obligatoire', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False),
    ],
    responses={
        200: enveloppe('defis', openapi.Schema(type=openapi.TYPE_ARRAY, items=DEFI_SCHEMA), avec_message=False),
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_detail_defi = swagger_auto_schema(
    operation_summary="Consulter le détail d'un défi",
    responses={
        200: enveloppe('defi', DEFI_SCHEMA, avec_message=False),
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_commencer_defi = swagger_auto_schema(
    operation_summary="Commencer un défi disponible",
    operation_description="Passe le statut de disponible à en_cours. Un défi verrouillé ne peut pas être commencé.",
    responses={
        200: enveloppe('defi', DEFI_SCHEMA),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_soumettre_activite = swagger_auto_schema(
    operation_summary="Envoyer les preuves d'une activité",
    operation_description=(
        "Requête multipart. Envoyer plusieurs fichiers en répétant la clé 'photos'. "
        "Le nombre de photos et l'obligation de vidéo dépendent de la configuration du défi."
    ),
    manual_parameters=[
        openapi.Parameter('rapport', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('date_activite', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True),
        openapi.Parameter('lieu', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('nombre_personnes_sensibilisees', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('photos', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True, description="Répéter cette clé pour envoyer plusieurs photos."),
        openapi.Parameter('video', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
    ],
    consumes=['multipart/form-data'],
    responses={
        201: enveloppe('soumission', SOUMISSION_SCHEMA),
        400: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_mes_soumissions = swagger_auto_schema(
    operation_summary="Lister l'historique de mes activités",
    manual_parameters=[
        openapi.Parameter('statut', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, enum=['en_attente', 'validee', 'refusee']),
        openapi.Parameter('defi_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
    ],
    responses={
        200: enveloppe('soumissions', openapi.Schema(type=openapi.TYPE_ARRAY, items=SOUMISSION_SCHEMA), avec_message=False),
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_detail_soumission = swagger_auto_schema(
    operation_summary="Consulter une de mes soumissions et le commentaire du validateur",
    responses={
        200: enveloppe('soumission', SOUMISSION_SCHEMA, avec_message=False),
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_annuler_soumission = swagger_auto_schema(
    operation_summary="Annuler une soumission encore en attente",
    responses={
        200: enveloppe('soumission', openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)),
        400: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)

swagger_mes_statistiques = swagger_auto_schema(
    operation_summary="Consulter mes statistiques de défis et d'impact",
    responses={
        200: enveloppe('statistiques', STATISTIQUES_UTILISATEUR_SCHEMA, avec_message=False),
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Ambassadeur'],
)


# =============================================================================
# ADMIN - DÉFIS
# =============================================================================

swagger_admin_liste_defis = swagger_auto_schema(
    operation_summary="[Admin] Lister tous les défis",
    manual_parameters=[
        openapi.Parameter('niveau', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('est_publie', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('est_actif', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('module_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
    ],
    responses={
        200: enveloppe('defis', openapi.Schema(type=openapi.TYPE_ARRAY, items=DEFI_ADMIN_SCHEMA), avec_message=False),
        403: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

def _defi_form_parameters(champs_requis):
    return [
        openapi.Parameter('module_id', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('titre', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('resultat_attendu', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('criteres_validation', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('image_couverture', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
        openapi.Parameter('niveau', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis, enum=['debutant', 'apprenti', 'actif', 'leader']),
        openapi.Parameter('ordre', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('duree_estimee', openapi.IN_FORM, type=openapi.TYPE_STRING, required=champs_requis),
        openapi.Parameter('points_recompense', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('nombre_photos_min', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('nombre_photos_max', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('video_obligatoire', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('est_obligatoire', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('est_actif', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('est_publie', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('est_ouvert', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('date_debut', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, required=False),
        openapi.Parameter('date_fin', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, required=False),
    ]


DEFI_FORM_PARAMETERS = _defi_form_parameters(True)

swagger_creer_defi = swagger_auto_schema(
    operation_summary="[Admin] Créer un défi",
    manual_parameters=DEFI_FORM_PARAMETERS,
    consumes=['multipart/form-data'],
    responses={
        201: enveloppe('defi', DEFI_ADMIN_SCHEMA),
        400: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_modifier_defi = swagger_auto_schema(
    operation_summary="[Admin] Modifier un défi",
    manual_parameters=_defi_form_parameters(False),
    consumes=['multipart/form-data'],
    responses={
        200: enveloppe('defi', DEFI_ADMIN_SCHEMA),
        400: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_supprimer_defi = swagger_auto_schema(
    operation_summary="[Admin] Supprimer un défi",
    responses={
        200: enveloppe('defi', openapi.Schema(type=openapi.TYPE_OBJECT, x_nullable=True)),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_ouvrir_defi = swagger_auto_schema(
    operation_summary="[Admin] Ouvrir manuellement un défi",
    responses={
        200: enveloppe('defi', DEFI_ADMIN_SCHEMA),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_fermer_defi = swagger_auto_schema(
    operation_summary="[Admin] Fermer manuellement un défi",
    responses={
        200: enveloppe('defi', DEFI_ADMIN_SCHEMA),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Admin'],
)

swagger_participants_defi = swagger_auto_schema(
    operation_summary="[Admin/Validateur] Lister les participants d'un défi",
    manual_parameters=[
        openapi.Parameter('statut', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
    ],
    responses={
        200: enveloppe('participants', openapi.Schema(type=openapi.TYPE_ARRAY, items=PARTICIPANT_SCHEMA), avec_message=False),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)


# =============================================================================
# ADMIN / VALIDATEUR - SOUMISSIONS
# =============================================================================

swagger_admin_liste_soumissions = swagger_auto_schema(
    operation_summary="[Admin/Validateur] Lister les soumissions",
    manual_parameters=[
        openapi.Parameter('statut', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('defi_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('utilisateur_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('recherche', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
    ],
    responses={
        200: enveloppe('soumissions', openapi.Schema(type=openapi.TYPE_ARRAY, items=SOUMISSION_SCHEMA), avec_message=False),
        403: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)

swagger_admin_detail_soumission = swagger_auto_schema(
    operation_summary="[Admin/Validateur] Consulter toutes les preuves d'une soumission",
    responses={
        200: enveloppe('soumission', SOUMISSION_SCHEMA, avec_message=False),
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)

swagger_valider_soumission = swagger_auto_schema(
    operation_summary="[Admin/Validateur] Accepter ou refuser une soumission",
    operation_description=(
        "L'acceptation termine le défi, attribue les points une seule fois, met à jour le niveau, "
        "le badge courant et la progression. Le commentaire est obligatoire en cas de refus."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['decision'],
        properties={
            'decision': openapi.Schema(type=openapi.TYPE_STRING, enum=['acceptee', 'refusee']),
            'commentaire': openapi.Schema(type=openapi.TYPE_STRING),
            'points_attribues': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Facultatif. Par défaut : points_recompense du défi.",
            ),
        },
    ),
    responses={
        200: enveloppe('soumission', SOUMISSION_SCHEMA),
        409: ERREUR_SCHEMA,
        403: ERREUR_SCHEMA,
        404: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)

swagger_admin_statistiques = swagger_auto_schema(
    operation_summary="[Admin/Validateur] Statistiques globales des défis et de l'impact",
    responses={
        200: enveloppe('statistiques', STATISTIQUES_ADMIN_SCHEMA, avec_message=False),
        403: ERREUR_SCHEMA,
        401: ERREUR_SCHEMA,
    },
    tags=['Challenges - Validation'],
)
