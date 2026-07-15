import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import status
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from rest_framework.response import Response
from .services import (
    ErreurQuiz,
)
from .models import (
    Choix,
    Module,
    Question,
    Quiz
)

logger = logging.getLogger(__name__)
 
# =============================================================================
# Réponses et helpers
# =============================================================================

def reponse_succes(nom_attribut, valeur, message=None, http_status=status.HTTP_200_OK):
    payload = {'success': True}
    if message:
        payload['message'] = message
    payload[nom_attribut] = valeur
    return Response(payload, status=http_status)


def reponse_erreur(message, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({'success': False, 'erreur': message}, status=http_status)


def _erreur_interne(exc):
    logger.exception("Erreur interne dans l'application formation", exc_info=exc)
    return reponse_erreur(
        "Une erreur interne est survenue.", status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def _bool(valeur, defaut=False):
    if valeur is None:
        return defaut
    if isinstance(valeur, bool):
        return valeur
    return str(valeur).strip().lower() in {'1', 'true', 'oui', 'yes', 'on'}


def _int(valeur, *, minimum=None, maximum=None, nom='valeur'):
    try:
        resultat = int(valeur)
    except (TypeError, ValueError) as exc:
        raise ErreurQuiz(f"Le champ '{nom}' doit être un entier.") from exc
    if minimum is not None and resultat < minimum:
        raise ErreurQuiz(f"Le champ '{nom}' doit être supérieur ou égal à {minimum}.")
    if maximum is not None and resultat > maximum:
        raise ErreurQuiz(f"Le champ '{nom}' doit être inférieur ou égal à {maximum}.")
    return resultat


def _datetime_ou_none(valeur, nom):
    if valeur in (None, ''):
        return None
    if hasattr(valeur, 'tzinfo'):
        return valeur
    resultat = parse_datetime(str(valeur))
    if resultat is None:
        raise ErreurQuiz(f"Le champ '{nom}' doit être une date ISO-8601 valide.")
    if timezone.is_naive(resultat):
        resultat = timezone.make_aware(resultat)
    return resultat


def _module_ambassadeur(module_slug):
    return Module.objects.filter(slug=module_slug, est_publie=True).first()


def _module_admin(module_slug):
    return Module.objects.filter(slug=module_slug).first()


def _quiz_admin(quiz_uuid):
    return Quiz.objects.select_related('module').filter(uuid=quiz_uuid).first()


def _question_admin(question_uuid):
    return Question.objects.select_related('quiz', 'quiz__module').filter(
        uuid=question_uuid
    ).first()


def _slug_unique(titre, module=None):
    base = slugify(titre) or 'module'
    slug = base
    index = 1
    queryset = Module.objects.all()
    if module is not None:
        queryset = queryset.exclude(pk=module.pk)
    while queryset.filter(slug=slug).exists():
        slug = f'{base}-{index}'
        index += 1
    return slug


def _valider_type_question(type_question):
    types = {valeur for valeur, _ in Question.TypeQuestion.choices}
    if type_question not in types:
        raise ErreurQuiz(
            "Type de question invalide. Valeurs : choix_unique, choix_multiple, reponse_courte."
        )


def _valider_configuration_question(*, type_question, choix, reponses_acceptees):
    _valider_type_question(type_question)
    if type_question == Question.TypeQuestion.REPONSE_COURTE:
        if not isinstance(reponses_acceptees, list) or not reponses_acceptees:
            raise ErreurQuiz(
                "Une question à réponse courte doit avoir une liste non vide "
                "'reponses_acceptees'."
            )
        return

    if not isinstance(choix, list) or len(choix) < 2:
        raise ErreurQuiz("Une question à choix doit contenir au moins deux choix.")
    corrects = [item for item in choix if _bool(item.get('est_correct'))]
    if type_question == Question.TypeQuestion.CHOIX_UNIQUE and len(corrects) != 1:
        raise ErreurQuiz("Une question à choix unique doit avoir exactement un choix correct.")
    if type_question == Question.TypeQuestion.CHOIX_MULTIPLE and not corrects:
        raise ErreurQuiz("Une question à choix multiple doit avoir au moins un choix correct.")
    for item in choix:
        if not str(item.get('texte') or '').strip():
            raise ErreurQuiz("Chaque choix doit contenir un texte non vide.")


def _creer_question(quiz, donnees, ordre_defaut=0):
    if not isinstance(donnees, dict):
        raise ErreurQuiz("Chaque question doit être un objet JSON.")
    texte = str(donnees.get('texte') or '').strip()
    if not texte:
        raise ErreurQuiz("Le champ 'texte' est requis pour chaque question.")
    type_question = donnees.get('type_question', Question.TypeQuestion.CHOIX_UNIQUE)
    choix = donnees.get('choix', [])
    reponses_acceptees = donnees.get('reponses_acceptees', [])
    _valider_configuration_question(
        type_question=type_question,
        choix=choix,
        reponses_acceptees=reponses_acceptees,
    )

    question = Question.objects.create(
        quiz=quiz,
        texte=texte,
        type_question=type_question,
        points=_int(donnees.get('points', 1), minimum=1, nom='points'),
        ordre=_int(donnees.get('ordre', ordre_defaut), minimum=0, nom='ordre'),
        explication=donnees.get('explication') or None,
        reponses_acceptees=(
            [str(v).strip() for v in reponses_acceptees]
            if type_question == Question.TypeQuestion.REPONSE_COURTE
            else []
        ),
        sensible_a_la_casse=(
            _bool(donnees.get('sensible_a_la_casse'))
            if type_question == Question.TypeQuestion.REPONSE_COURTE
            else False
        ),
    )
    if type_question != Question.TypeQuestion.REPONSE_COURTE:
        Choix.objects.bulk_create([
            Choix(
                question=question,
                texte=str(item.get('texte')).strip(),
                est_correct=_bool(item.get('est_correct')),
                explication=item.get('explication') or None,
            )
            for item in choix
        ])
    return question


def _modifier_question(question, donnees):
    if question.tirages.exists() or question.reponses.exists():
        raise ErreurQuiz(
            "Cette question a déjà été utilisée dans une tentative. Elle ne peut plus être "
            "modifiée afin de préserver l'historique. Ajoutez une nouvelle question à la banque."
        )

    type_question = donnees.get('type_question', question.type_question)
    choix_fournis = 'choix' in donnees
    if choix_fournis:
        choix = donnees.get('choix')
    else:
        choix = [
            {
                'texte': item.texte,
                'est_correct': item.est_correct,
                'explication': item.explication,
            }
            for item in question.choix.all()
        ]
    reponses_acceptees = donnees.get(
        'reponses_acceptees', question.reponses_acceptees
    )
    _valider_configuration_question(
        type_question=type_question,
        choix=choix,
        reponses_acceptees=reponses_acceptees,
    )

    if 'texte' in donnees:
        texte = str(donnees.get('texte') or '').strip()
        if not texte:
            raise ErreurQuiz("Le champ 'texte' ne peut pas être vide.")
        question.texte = texte
    question.type_question = type_question
    if 'points' in donnees:
        question.points = _int(donnees.get('points'), minimum=1, nom='points')
    if 'ordre' in donnees:
        question.ordre = _int(donnees.get('ordre'), minimum=0, nom='ordre')
    if 'explication' in donnees:
        question.explication = donnees.get('explication') or None

    if type_question == Question.TypeQuestion.REPONSE_COURTE:
        question.reponses_acceptees = [str(v).strip() for v in reponses_acceptees]
        question.sensible_a_la_casse = _bool(
            donnees.get('sensible_a_la_casse', question.sensible_a_la_casse)
        )
    else:
        question.reponses_acceptees = []
        question.sensible_a_la_casse = False
    question.full_clean()
    question.save()

    if type_question == Question.TypeQuestion.REPONSE_COURTE:
        question.choix.all().delete()
    elif choix_fournis or not question.choix.exists():
        question.choix.all().delete()
        Choix.objects.bulk_create([
            Choix(
                question=question,
                texte=str(item.get('texte')).strip(),
                est_correct=_bool(item.get('est_correct')),
                explication=item.get('explication') or None,
            )
            for item in choix
        ])
    return question
