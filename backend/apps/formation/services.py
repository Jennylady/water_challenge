import random
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import (
    Choix,
    ProgressionModule,
    Question,
    QuestionTentative,
    ReponseQuiz,
    TentativeQuiz,
)


POINTS_GAMIFICATION_PAR_MODULE_REUSSI = 20


class ErreurQuiz(Exception):
    """Erreur métier affichable au client."""


@dataclass
class ResultatEvaluation:
    est_correcte: bool
    points_obtenus: int
    choix: list
    reponse_texte: str | None
    correction: dict | None
    explication: str | None


def _normaliser_texte(valeur):
    return str(valeur or '').strip()


def _explication_question(question, choix_selectionnes=None):
    """Retourne l'explication la plus pertinente sans doublon."""
    explications = []
    if question.explication:
        explications.append(question.explication)

    # Une explication attachée au choix sélectionné peut préciser pourquoi il est faux.
    for choix in choix_selectionnes or []:
        if choix.explication:
            explications.append(choix.explication)

    # À défaut, les explications des bonnes réponses expliquent la correction attendue.
    for choix in question.choix.filter(est_correct=True):
        if choix.explication:
            explications.append(choix.explication)

    uniques = []
    for explication in explications:
        texte = str(explication).strip()
        if texte and texte not in uniques:
            uniques.append(texte)
    return '\n'.join(uniques) or None


def _correction_question(question):
    if question.type_question == Question.TypeQuestion.REPONSE_COURTE:
        return {
            'type_question': question.type_question,
            'reponses_acceptees': list(question.reponses_acceptees or []),
        }
    return {
        'type_question': question.type_question,
        'choix_corrects': [
            {'id': choix.uuid, 'texte': choix.texte}
            for choix in question.choix.filter(est_correct=True)
        ],
    }


def evaluer_reponse(question, *, choix_ids=None, reponse_texte=None):
    """Valide le format reçu puis calcule la correction côté serveur."""
    if question.type_question == Question.TypeQuestion.REPONSE_COURTE:
        if reponse_texte is None:
            raise ErreurQuiz("Le champ 'reponse_texte' est requis pour cette question.")
        texte = _normaliser_texte(reponse_texte)
        attendues = [str(v) for v in (question.reponses_acceptees or [])]
        if question.sensible_a_la_casse:
            est_correcte = texte in attendues
        else:
            est_correcte = texte.casefold() in [v.casefold() for v in attendues]
        return ResultatEvaluation(
            est_correcte=est_correcte,
            points_obtenus=question.points if est_correcte else 0,
            choix=[],
            reponse_texte=texte,
            correction=None if est_correcte else _correction_question(question),
            explication=None if est_correcte else _explication_question(question),
        )

    if not isinstance(choix_ids, list) or not choix_ids:
        raise ErreurQuiz("Le champ 'choix_ids' doit être une liste non vide.")
    if question.type_question == Question.TypeQuestion.CHOIX_UNIQUE and len(choix_ids) != 1:
        raise ErreurQuiz("Cette question attend exactement un choix.")

    # Les UUID sont recherchés uniquement dans les choix appartenant à la question.
    choix = list(question.choix.filter(uuid__in=choix_ids))
    if len(choix) != len(set(str(v) for v in choix_ids)):
        raise ErreurQuiz("Un ou plusieurs choix sont invalides pour cette question.")

    ids_selectionnes = {c.uuid for c in choix}
    ids_corrects = set(question.choix.filter(est_correct=True).values_list('uuid', flat=True))
    est_correcte = ids_selectionnes == ids_corrects
    return ResultatEvaluation(
        est_correcte=est_correcte,
        points_obtenus=question.points if est_correcte else 0,
        choix=choix,
        reponse_texte=None,
        correction=None if est_correcte else _correction_question(question),
        explication=(
            None if est_correcte
            else _explication_question(question, choix_selectionnes=choix)
        ),
    )


def demarrer_ou_reprendre_tentative(utilisateur, quiz):
    """
    Retourne l'unique tentative en cours. Si elle n'existe pas, tire aléatoirement
    les questions puis persiste le tirage afin qu'un rechargement ne le modifie pas.
    """
    with transaction.atomic():
        # Le verrou sur le quiz évite deux créations concurrentes pour le même utilisateur.
        quiz_verrouille = quiz.__class__.objects.select_for_update().get(pk=quiz.pk)
        tentative = TentativeQuiz.objects.filter(
            utilisateur=utilisateur,
            quiz=quiz_verrouille,
            statut=TentativeQuiz.Statut.EN_COURS,
        ).first()
        if tentative:
            return tentative, False

        questions = list(quiz_verrouille.questions.all())
        if not questions:
            raise ErreurQuiz("La banque de questions de ce quiz est vide.")
        if quiz_verrouille.nombre_questions > len(questions):
            raise ErreurQuiz(
                "Le nombre de questions demandé est supérieur au nombre de questions "
                "disponibles dans la banque."
            )

        selection = random.SystemRandom().sample(
            questions, quiz_verrouille.nombre_questions
        )
        try:
            # Savepoint imbriqué : en cas de collision sur la contrainte unique,
            # l'atomic externe reste utilisable pour relire la tentative concurrente.
            with transaction.atomic():
                tentative = TentativeQuiz.objects.create(
                    utilisateur=utilisateur,
                    quiz=quiz_verrouille,
                    points_total=sum(q.points for q in selection),
                )
        except IntegrityError:
            tentative = TentativeQuiz.objects.get(
                utilisateur=utilisateur,
                quiz=quiz_verrouille,
                statut=TentativeQuiz.Statut.EN_COURS,
            )
            return tentative, False

        QuestionTentative.objects.bulk_create([
            QuestionTentative(tentative=tentative, question=question, ordre=index)
            for index, question in enumerate(selection, start=1)
        ])
        return tentative, True


def enregistrer_reponse(*, tentative, question, choix_ids=None, reponse_texte=None):
    if tentative.statut != TentativeQuiz.Statut.EN_COURS:
        raise ErreurQuiz("Cette tentative a déjà été soumise.")
    if not tentative.questions_selectionnees.filter(question=question).exists():
        raise ErreurQuiz("Cette question ne fait pas partie de cette tentative.")

    resultat = evaluer_reponse(
        question, choix_ids=choix_ids, reponse_texte=reponse_texte
    )
    with transaction.atomic():
        reponse, _ = ReponseQuiz.objects.update_or_create(
            tentative=tentative,
            question=question,
            defaults={
                'reponse_texte': resultat.reponse_texte,
                'est_correcte': resultat.est_correcte,
                'points_obtenus': resultat.points_obtenus,
            },
        )
        reponse.choix_selectionnes.set(resultat.choix)
    return reponse, resultat


def _reevaluer_reponse(reponse):
    question = reponse.question
    if question.type_question == Question.TypeQuestion.REPONSE_COURTE:
        return evaluer_reponse(question, reponse_texte=reponse.reponse_texte)
    return evaluer_reponse(
        question,
        choix_ids=[str(c.uuid) for c in reponse.choix_selectionnes.all()],
    )


def soumettre_tentative(*, tentative, utilisateur):
    """Note la tentative à partir des réponses sauvegardées, une seule fois."""
    with transaction.atomic():
        tentative = TentativeQuiz.objects.select_for_update().select_related(
            'quiz', 'quiz__module'
        ).get(pk=tentative.pk, utilisateur=utilisateur)
        if tentative.statut != TentativeQuiz.Statut.EN_COURS:
            raise ErreurQuiz("Cette tentative a déjà été soumise.")

        tirages = list(
            tentative.questions_selectionnees.select_related('question').order_by('ordre')
        )
        reponses = {
            r.question_id: r
            for r in tentative.reponses.select_related('question').prefetch_related(
                'choix_selectionnes'
            )
        }
        manquantes = [
            str(t.question.uuid) for t in tirages if t.question_id not in reponses
        ]
        if manquantes:
            raise ErreurQuiz(
                "Toutes les questions doivent être répondues avant la soumission. "
                f"Questions manquantes : {', '.join(manquantes)}"
            )

        points_total = 0
        points_obtenus = 0
        reponses_modifiees = []
        for tirage in tirages:
            question = tirage.question
            reponse = reponses[question.pk]
            resultat = _reevaluer_reponse(reponse)
            reponse.est_correcte = resultat.est_correcte
            reponse.points_obtenus = resultat.points_obtenus
            reponses_modifiees.append(reponse)
            points_total += question.points
            points_obtenus += resultat.points_obtenus

        ReponseQuiz.objects.bulk_update(
            reponses_modifiees, ['est_correcte', 'points_obtenus']
        )
        score = round((points_obtenus / points_total) * 100) if points_total else 0
        est_reussi = score >= tentative.quiz.score_de_reussite

        tentative.points_total = points_total
        tentative.points_obtenus = points_obtenus
        tentative.score = score
        tentative.est_reussi = est_reussi
        tentative.statut = TentativeQuiz.Statut.SOUMISE
        tentative.soumise_le = timezone.now()
        tentative.save(update_fields=[
            'points_total', 'points_obtenus', 'score', 'est_reussi',
            'statut', 'soumise_le',
        ])

        if est_reussi:
            from apps.recompenses.services import synchroniser_progression_module
            transaction.on_commit(
                lambda: synchroniser_progression_module(utilisateur, tentative.quiz.module)
            )

        return tentative


def charger_progressions_utilisateur(utilisateur, modules):
    """
    Reconstitue la progression à partir des actions déjà enregistrées.

    La lecture, la réussite du quiz et les défis terminés sont indépendants :
    aucune étape ne sert de prérequis à une autre.
    """
    modules = list(modules)
    if not modules:
        return {}

    module_ids = {module.id for module in modules}
    progressions = {
        progression.module_id: progression
        for progression in ProgressionModule.objects.filter(
            utilisateur_id=utilisateur.id,
            module_id__in=module_ids,
        )
    }

    modules_avec_activite = set(
        TentativeQuiz.objects.filter(
            utilisateur_id=utilisateur.id,
            est_reussi=True,
            quiz__module_id__in=module_ids,
        ).values_list('quiz__module_id', flat=True)
    )
    modules_avec_activite.update(
        utilisateur.defis_utilisateur.filter(
            statut='termine',
            defi__module_id__in=module_ids,
        ).values_list('defi__module_id', flat=True)
    )

    modules_par_id = {module.id: module for module in modules}
    for module_id in modules_avec_activite:
        if module_id not in progressions:
            progression, _ = ProgressionModule.objects.get_or_create(
                utilisateur_id=utilisateur.id,
                module=modules_par_id[module_id],
            )
            progressions[module_id] = progression

    for progression in progressions.values():
        progression.recalculer()
    return progressions
