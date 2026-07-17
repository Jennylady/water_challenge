import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'framer-motion'

import { getApiErrorMessage } from '../../api/api'
import { formationApi } from '../../api/services'

import './Quiz.css'

const fetchQuizData = async (moduleSlug) =>
  formationApi.getQuiz(moduleSlug)

const saveReponse = async (
  tentativeId,
  questionId,
  payload
) =>
  formationApi.answerQuestion(
    tentativeId,
    questionId,
    payload
  )

const submitTentative = async (tentativeId) =>
  formationApi.submitAttempt(tentativeId)

// ---------------------------------------------------------------------------
// Helpers de normalisation des données (compatibles avec les champs FR
// renvoyés par l'API : texte, choix, bonnes_reponses, est_correcte, etc.)
// ---------------------------------------------------------------------------

const getModuleSlug = (module) =>
  String(module?.slug || '').trim()

const getQuestionId = (
  question,
  questionIndex
) =>
  String(
    question?.id ??
      question?.uuid ??
      question?.ordre ??
      questionIndex
  )

const getQuestionText = (
  question,
  questionIndex
) =>
  question?.texte ||
  question?.question ||
  question?.libelle ||
  question?.titre ||
  `Question ${questionIndex + 1}`

const getQuestionExplanation = (question) =>
  question?.explication ||
  question?.explanation ||
  question?.correction ||
  ''

const getQuestionOptions = (question) => {
  const options =
    question?.options ??
    question?.reponses ??
    question?.choix ??
    question?.answers ??
    []

  if (Array.isArray(options)) {
    return options
  }

  if (
    options &&
    typeof options === 'object'
  ) {
    return Object.entries(options).map(
      ([key, value]) => {
        if (
          value &&
          typeof value === 'object'
        ) {
          return {
            id: value.id ?? key,
            ...value,
          }
        }

        return {
          id: key,
          texte: value,
        }
      }
    )
  }

  return []
}

const getOptionId = (
  option,
  optionIndex
) => {
  if (
    option === null ||
    option === undefined
  ) {
    return String(optionIndex)
  }

  if (
    typeof option === 'string' ||
    typeof option === 'number'
  ) {
    return String(optionIndex)
  }

  return String(
    option.id ??
      option.uuid ??
      option.value ??
      option.code ??
      optionIndex
  )
}

const getOptionText = (
  option,
  optionIndex
) => {
  if (
    typeof option === 'string' ||
    typeof option === 'number'
  ) {
    return String(option)
  }

  return (
    option?.texte ||
    option?.libelle ||
    option?.label ||
    option?.reponse ||
    option?.answer ||
    option?.value ||
    `Réponse ${optionIndex + 1}`
  )
}

const getQuestionType = (question) =>
  String(
    question?.type_question ||
      question?.type ||
      question?.question_type ||
      ''
  ).toLowerCase()

const isShortAnswerQuestion = (question) => {
  const type = getQuestionType(question)

  return Boolean(
    type === 'reponse_courte' ||
      question?.reponse_libre ||
      question?.texte_libre
  )
}

const isMultipleQuestion = (question) => {
  const type = getQuestionType(question)

  return Boolean(
    question?.multiple ||
      question?.plusieurs_reponses ||
      question?.choix_multiple ||
      type === 'multiple' ||
      type === 'checkbox' ||
      type === 'choix_multiple'
  )
}

// Best-effort : si l'API renvoie déjà une réponse enregistrée dans l'objet
// question (nom de champ non spécifié dans la doc), on la récupère pour
// pré-remplir l'état local après un rechargement de page.
const getExistingAnswerState = (question) => {
  const savedChoiceIds =
    question?.choix_ids ??
    question?.reponse_choix_ids ??
    question?.mes_choix ??
    question?.reponse_enregistree?.choix_ids ??
    question?.reponse_utilisateur?.choix_ids

  const savedText =
    question?.reponse_texte ??
    question?.ma_reponse ??
    question?.reponse_enregistree?.reponse_texte ??
    question?.reponse_utilisateur?.reponse_texte

  const rawResult =
    question?.reponse_utilisateur ??
    question?.ma_reponse_correction

  const result =
    rawResult &&
    typeof rawResult?.est_correcte === 'boolean'
      ? {
          estCorrecte: rawResult.est_correcte,
          correction: rawResult.correction,
          explication: rawResult.explication,
        }
      : null

  if (
    !savedChoiceIds &&
    !savedText &&
    !result
  ) {
    return null
  }

  return {
    choixIds: Array.isArray(savedChoiceIds)
      ? savedChoiceIds.map(String)
      : undefined,
    reponseTexte: savedText
      ? String(savedText)
      : undefined,
    result,
  }
}

const isAnswerFilled = (value) =>
  Array.isArray(value)
    ? value.length > 0
    : Boolean(
        value && String(value).trim()
      )

const toFiniteNumber = (value, fallback = 0) => {
  const number = Number(value)
  return Number.isFinite(number) ? number : fallback
}

// Le champ "correction" renvoyé par l'API a une forme libre (schéma = {}).
// On essaie plusieurs formes courantes pour en tirer un texte lisible.
const formatCorrectionAnswer = (
  correction,
  options
) => {
  if (!correction) {
    return ''
  }

  if (typeof correction === 'string') {
    return correction
  }

  const correctIds =
    correction?.choix_ids ??
    correction?.reponse_correcte ??
    correction?.bonnes_reponses ??
    correction?.correct_answer

  const idsList = Array.isArray(
    correctIds
  )
    ? correctIds
    : correctIds !== undefined &&
        correctIds !== null
      ? [correctIds]
      : []

  if (idsList.length > 0) {
    return idsList
      .map((id) => {
        const optionIndex =
          options.findIndex(
            (option, index) =>
              getOptionId(
                option,
                index
              ) === String(id)
          )

        return optionIndex >= 0
          ? getOptionText(
              options[optionIndex],
              optionIndex
            )
          : String(id)
      })
      .join(', ')
  }

  return (
    correction?.texte ||
    correction?.reponse_texte ||
    ''
  )
}

function Quiz({
  module,
  onBack,
  onOpenLesson,
  onOpenChallenge,
  onSubmit,
}) {
  const [quiz, setQuiz] = useState(null)
  const [isLoadingQuiz, setIsLoadingQuiz] =
    useState(true)
  const [loadError, setLoadError] =
    useState('')
  const [reloadToken, setReloadToken] =
    useState(0)

  const [activeQuestionIndex, setActiveQuestionIndex] =
    useState(0)

  // valeur = tableau d'ids (QCM/QCU) ou string (réponse courte)
  const [answers, setAnswers] =
    useState({})

  const [shortAnswerDrafts, setShortAnswerDrafts] =
    useState({})

  // questionId -> { estCorrecte, correction, explication }
  const [questionResults, setQuestionResults] =
    useState({})

  const [savingQuestionIds, setSavingQuestionIds] =
    useState({})

  const [saveError, setSaveError] =
    useState('')

  const [submission, setSubmission] = useState(null)
  const [showResultModal, setShowResultModal] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [attempts, setAttempts] = useState([])
  const [ranking, setRanking] = useState([])
  const [sideDataError, setSideDataError] = useState('')

  const hasNotifiedSubmitRef = useRef(false)

  const questions = quiz?.questions || []

  const moduleSlug =
    getModuleSlug(module)

  // ---------------------------------------------------------------------
  // Chargement du quiz depuis l'API
  // ---------------------------------------------------------------------
  useEffect(() => {
    let isCancelled = false

    setAnswers({})
    setShortAnswerDrafts({})
    setQuestionResults({})
    setSavingQuestionIds({})
    setSaveError('')
    setSubmission(null)
    setShowResultModal(false)
    setActiveQuestionIndex(0)
    hasNotifiedSubmitRef.current = false

    if (!moduleSlug) {
      setQuiz(null)
      setIsLoadingQuiz(false)
      setLoadError('')

      return undefined
    }

    setIsLoadingQuiz(true)
    setLoadError('')

    fetchQuizData(moduleSlug)
      .then((fetchedQuiz) => {
        if (isCancelled) return

        setQuiz(fetchedQuiz || null)

        const initialAnswers = {}
        const initialDrafts = {}
        const initialResults = {}

        ;(fetchedQuiz?.questions || []).forEach(
          (question, questionIndex) => {
            const questionId = getQuestionId(
              question,
              questionIndex
            )

            const existing =
              getExistingAnswerState(question)

            if (!existing) return

            if (existing.choixIds?.length) {
              initialAnswers[questionId] =
                existing.choixIds
            } else if (
              existing.reponseTexte
            ) {
              initialAnswers[questionId] =
                existing.reponseTexte
              initialDrafts[questionId] =
                existing.reponseTexte
            }

            if (existing.result) {
              initialResults[questionId] =
                existing.result
            }
          }
        )

        setAnswers(initialAnswers)
        setShortAnswerDrafts(initialDrafts)
        setQuestionResults(initialResults)
      })
      .catch((error) => {
        if (isCancelled) return

        console.error(
          'Erreur lors du chargement du quiz :',
          error
        )

        setLoadError(
          error?.response?.data?.erreur ||
            error?.response?.data?.detail ||
            error?.message ||
            'Impossible de charger le quiz.'
        )
      })
      .finally(() => {
        if (!isCancelled) {
          setIsLoadingQuiz(false)
        }
      })

    return () => {
      isCancelled = true
    }
  }, [moduleSlug, reloadToken])

  useEffect(() => {
    let cancelled = false

    if (!moduleSlug) {
      setAttempts([])
      setRanking([])
      return undefined
    }

    setSideDataError('')

    Promise.allSettled([
      formationApi.listAttempts(moduleSlug),
      formationApi.getRanking(moduleSlug),
    ]).then(([attemptsResult, rankingResult]) => {
      if (cancelled) {
        return
      }

      if (attemptsResult.status === 'fulfilled') {
        setAttempts(
          Array.isArray(attemptsResult.value)
            ? attemptsResult.value
            : []
        )
      }

      if (rankingResult.status === 'fulfilled') {
        setRanking(
          Array.isArray(rankingResult.value)
            ? rankingResult.value
            : []
        )
      }

      if (
        attemptsResult.status === 'rejected' &&
        rankingResult.status === 'rejected'
      ) {
        setSideDataError(
          'Historique et classement indisponibles pour le moment.'
        )
      }
    })

    return () => {
      cancelled = true
    }
  }, [moduleSlug, reloadToken])

  const currentQuestion =
    questions[activeQuestionIndex]

  const currentQuestionId =
    currentQuestion
      ? getQuestionId(
          currentQuestion,
          activeQuestionIndex
        )
      : ''

  const currentOptions =
    currentQuestion
      ? getQuestionOptions(currentQuestion)
      : []

  const isCurrentShortAnswer =
    currentQuestion
      ? isShortAnswerQuestion(
          currentQuestion
        )
      : false

  const currentAnswers = Array.isArray(
    answers[currentQuestionId]
  )
    ? answers[currentQuestionId]
    : []

  const currentResult =
    questionResults[currentQuestionId]

  const isSavingCurrent = Boolean(
    savingQuestionIds[currentQuestionId]
  )

  const answeredQuestionsCount =
    useMemo(() => {
      return questions.filter(
        (question, questionIndex) => {
          const questionId = getQuestionId(
            question,
            questionIndex
          )

          return isAnswerFilled(
            answers[questionId]
          )
        }
      ).length
    }, [answers, questions])

  const progress =
    questions.length > 0
      ? Math.round(
          (answeredQuestionsCount /
            questions.length) *
            100
        )
      : 0

  const allAnswersCompleted =
    questions.length > 0 &&
    answeredQuestionsCount === questions.length

  const isFinished = Boolean(
    submission ||
      (quiz?.statut_tentative &&
        quiz.statut_tentative !== 'en_cours')
  )

  const scoreSummary = useMemo(() => {
    if (submission) {
      const submittedResponses = Array.isArray(submission.reponses)
        ? submission.reponses
        : []

      const correctFromResponses = submittedResponses.filter(
        (response) => response?.est_correcte === true
      ).length
      const incorrectFromResponses = submittedResponses.filter(
        (response) => response?.est_correcte === false
      ).length

      const total = toFiniteNumber(
        submission.nombre_questions,
        questions.length
      )
      const answered = toFiniteNumber(
        submission.nombre_reponses,
        submittedResponses.length
      )
      const correct = toFiniteNumber(
        submission.nombre_bonnes_reponses,
        correctFromResponses
      )
      const incorrect = toFiniteNumber(
        submission.nombre_mauvaises_reponses,
        incorrectFromResponses || Math.max(answered - correct, 0)
      )

      return {
        correct,
        incorrect,
        answered,
        total,
        percentage: toFiniteNumber(submission.score, 0),
        successPercentage: toFiniteNumber(
          submission.score_de_reussite,
          toFiniteNumber(quiz?.score_de_reussite, 0)
        ),
        points: toFiniteNumber(submission.points_obtenus, 0),
        pointsTotal: toFiniteNumber(submission.points_total, 0),
      }
    }

    const correctedEntries = Object.values(
      questionResults
    ).filter(
      (result) =>
        typeof result?.estCorrecte === 'boolean'
    )

    if (correctedEntries.length === 0) {
      return null
    }

    const correct = correctedEntries.filter(
      (result) => result.estCorrecte
    ).length
    const incorrect = correctedEntries.length - correct

    return {
      correct,
      incorrect,
      answered: correctedEntries.length,
      total: questions.length || correctedEntries.length,
      percentage: Math.round(
        (correct / correctedEntries.length) * 100
      ),
      successPercentage: toFiniteNumber(quiz?.score_de_reussite, 0),
    }
  }, [questionResults, questions.length, quiz?.score_de_reussite, submission])


  const isSuccess = submission
    ? Boolean(submission.est_reussi)
    : null

  useEffect(() => {
    if (
      submission &&
      !hasNotifiedSubmitRef.current &&
      typeof onSubmit === 'function'
    ) {
      hasNotifiedSubmitRef.current = true

      onSubmit({
        moduleSlug,
        quizId: quiz?.id,
        tentativeId: submission.id || quiz?.tentative_id,
        totalQuestions: questions.length,
        score: scoreSummary,
        tentative: submission,
      })
    }
  }, [
    moduleSlug,
    onSubmit,
    questions.length,
    quiz?.id,
    quiz?.tentative_id,
    scoreSummary,
    submission,
  ])


  const saveAnswerToServer = async (
    question,
    questionIndex,
    payload
  ) => {
    const questionId = getQuestionId(
      question,
      questionIndex
    )

    if (!quiz?.tentative_id) {
      setSaveError(
        "Aucune tentative de quiz active."
      )

      return
    }

    setSavingQuestionIds((current) => ({
      ...current,
      [questionId]: true,
    }))

    setSaveError('')

    try {
      const reponse = await saveReponse(
        quiz.tentative_id,
        questionId,
        payload
      )

      if (
        reponse &&
        typeof reponse.est_correcte ===
          'boolean'
      ) {
        setQuestionResults((current) => ({
          ...current,
          [questionId]: {
            estCorrecte:
              reponse.est_correcte,
            correction:
              reponse.correction,
            explication:
              reponse.explication,
          },
        }))
      }
    } catch (error) {
      console.error(
        "Erreur pendant l'enregistrement de la réponse :",
        error
      )

      setSaveError(
        error?.response?.data?.erreur ||
          error?.response?.data?.detail ||
          error?.response?.data?.message ||
          error?.message ||
          "Impossible d'enregistrer votre réponse."
      )
    } finally {
      setSavingQuestionIds((current) => ({
        ...current,
        [questionId]: false,
      }))
    }
  }

  const handleSelectOption = (
    question,
    questionIndex,
    option,
    optionIndex
  ) => {
    if (isFinished) {
      return
    }

    const questionId = getQuestionId(
      question,
      questionIndex
    )

    const optionId = getOptionId(
      option,
      optionIndex
    )

    const multiple =
      isMultipleQuestion(question)

    const previous =
      answers[questionId]

    const previousList = Array.isArray(
      previous
    )
      ? previous
      : []

    const nextList = !multiple
      ? [optionId]
      : previousList.includes(optionId)
        ? previousList.filter(
            (id) => id !== optionId
          )
        : [...previousList, optionId]

    setAnswers((current) => ({
      ...current,
      [questionId]: nextList,
    }))

    saveAnswerToServer(
      question,
      questionIndex,
      { choix_ids: nextList }
    )
  }

  const handleShortAnswerChange = (
    question,
    questionIndex,
    value
  ) => {
    const questionId = getQuestionId(
      question,
      questionIndex
    )

    setShortAnswerDrafts((current) => ({
      ...current,
      [questionId]: value,
    }))
  }

  const handleShortAnswerSubmit = (
    question,
    questionIndex
  ) => {
    const questionId = getQuestionId(
      question,
      questionIndex
    )

    const value = (
      shortAnswerDrafts[questionId] ?? ''
    ).trim()

    if (!value) {
      return
    }

    setAnswers((current) => ({
      ...current,
      [questionId]: value,
    }))

    saveAnswerToServer(
      question,
      questionIndex,
      { reponse_texte: value }
    )
  }

  const handleSubmitAttempt = async () => {
    if (
      !quiz?.tentative_id ||
      !allAnswersCompleted ||
      isSubmitting ||
      Object.values(savingQuestionIds).some(Boolean)
    ) {
      return
    }

    setIsSubmitting(true)
    setSaveError('')

    try {
      const tentative = await submitTentative(
        quiz.tentative_id
      )

      const submittedResults = {}

      ;(Array.isArray(tentative?.reponses)
        ? tentative.reponses
        : []
      ).forEach((response) => {
        const responseQuestionId = String(
          response?.question_id || ''
        )

        if (!responseQuestionId) return

        submittedResults[responseQuestionId] = {
          estCorrecte:
            response?.est_correcte === true,
          correction: response?.correction,
          explication: response?.explication,
        }
      })

      setQuestionResults((current) => ({
        ...current,
        ...submittedResults,
      }))
      setSubmission(tentative)
      setShowResultModal(true)
      setQuiz((current) => ({
        ...current,
        statut_tentative: tentative?.statut || 'soumise',
      }))
      setAttempts((current) => [
        tentative,
        ...current.filter(
          (item) => String(item?.id) !== String(tentative?.id)
        ),
      ])

      window.dispatchEvent(
        new CustomEvent('waterchallenge:data-updated', {
          detail: {
            source: 'quiz-submitted',
            moduleSlug,
            tentativeId: tentative?.id || quiz.tentative_id,
          },
        })
      )
    } catch (error) {
      setSaveError(
        getApiErrorMessage(
          error,
          'Impossible de soumettre le quiz.'
        )
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePreviousQuestion = () => {
    setActiveQuestionIndex(
      (currentIndex) =>
        Math.max(currentIndex - 1, 0)
    )
  }

  const handleNextQuestion = () => {
    setActiveQuestionIndex(
      (currentIndex) =>
        Math.min(
          currentIndex + 1,
          questions.length - 1
        )
    )
  }

  const handleSelectQuestion = (index) => {
    setActiveQuestionIndex(index)
  }

  const handleRestart = () => {
    setShowResultModal(false)
    setSubmission(null)
    hasNotifiedSubmitRef.current = false
    setReloadToken(
      (currentToken) => currentToken + 1
    )

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  const resultModal =
    submission &&
    scoreSummary &&
    showResultModal &&
    typeof document !== 'undefined'
      ? createPortal(
          <AnimatePresence>
            <motion.div
              className="quiz-result-modal__overlay"
              role="presentation"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowResultModal(false)}
            >
              <motion.section
                className={[
                  'quiz-result-modal',
                  isSuccess
                    ? 'is-success'
                    : 'is-failure',
                ].join(' ')}
                role="dialog"
                aria-modal="true"
                aria-labelledby="quiz-result-modal-title"
                initial={{ opacity: 0, y: 28, scale: 0.94 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 20, scale: 0.96 }}
                transition={{ duration: 0.28, ease: 'easeOut' }}
                onClick={(event) => event.stopPropagation()}
              >
                <button
                  type="button"
                  className="quiz-result-modal__close"
                  aria-label="Fermer le résultat du quiz"
                  onClick={() => setShowResultModal(false)}
                >
                  ×
                </button>

                <div className="quiz-result-modal__heading">
                  <span
                    className="quiz-result-modal__icon"
                    aria-hidden="true"
                  >
                    {isSuccess ? '🎉' : '💪'}
                  </span>

                  <div>
                    <p className="quiz-result-modal__eyebrow">
                      Résultat de votre tentative
                    </p>

                    <h2 id="quiz-result-modal-title">
                      {isSuccess
                        ? 'Quiz réussi !'
                        : 'Quiz non réussi'}
                    </h2>

                    <p>
                      {submission?.message ||
                        (isSuccess
                          ? 'Bravo, vous pouvez maintenant passer aux défis de ce module.'
                          : 'Le seuil de réussite n’est pas encore atteint. Consultez vos réponses avant de continuer.')}
                    </p>
                  </div>
                </div>

                <div className="quiz-result-modal__body">
                  <div className="quiz-result-modal__score">
                    <strong>{scoreSummary.percentage}%</strong>
                    <span>Score obtenu</span>
                  </div>

                  <div className="quiz-result-modal__stats">
                    <div>
                      <span>Points</span>
                      <strong>
                        {scoreSummary.points}
                        {' / '}
                        {scoreSummary.pointsTotal}
                      </strong>
                    </div>

                    <div>
                      <span>Seuil de réussite</span>
                      <strong>
                        {scoreSummary.successPercentage}%
                      </strong>
                    </div>

                    <div className="is-correct">
                      <span>Bonnes réponses</span>
                      <strong>{scoreSummary.correct}</strong>
                    </div>

                    <div className="is-incorrect">
                      <span>Mauvaises réponses</span>
                      <strong>{scoreSummary.incorrect}</strong>
                    </div>

                    <div className="is-wide">
                      <span>Questions répondues</span>
                      <strong>
                        {scoreSummary.answered}
                        {' / '}
                        {scoreSummary.total}
                      </strong>
                    </div>
                  </div>
                </div>

                <div className="quiz-result-modal__actions">
                  <button
                    type="button"
                    className="is-secondary"
                    onClick={() => setShowResultModal(false)}
                  >
                    Consulter mes réponses
                  </button>

                  <button
                    type="button"
                    className="is-primary"
                    onClick={() => {
                      setShowResultModal(false)
                      onOpenChallenge?.()
                    }}
                  >
                    Quitter et voir les défis →
                  </button>
                </div>
              </motion.section>
            </motion.div>
          </AnimatePresence>,
          document.body
        )
      : null

  if (!module) {
    return (
      <section className="quiz-page">
        <div className="quiz-page__empty">
          <span aria-hidden="true">
            ⚠️
          </span>

          <h1>Module introuvable</h1>

          <p>
            Aucun module n’a été sélectionné
            pour afficher ce quiz.
          </p>

          {typeof onBack ===
            'function' && (
            <button
              type="button"
              onClick={onBack}
            >
              Retour aux modules
            </button>
          )}
        </div>
      </section>
    )
  }

  if (isLoadingQuiz) {
    return (
      <section className="quiz-page">
        <div className="quiz-page__empty quiz-page__loading">
          <span aria-hidden="true">
            ⏳
          </span>

          <h2>Chargement du quiz…</h2>
        </div>
      </section>
    )
  }

  if (loadError) {
    return (
      <section className="quiz-page">
        <div className="quiz-page__empty quiz-page__load-error">
          <span aria-hidden="true">
            ⚠️
          </span>

          <h2>Impossible de charger le quiz</h2>

          <p>{loadError}</p>

          <div className="quiz-page__empty-actions">
            <button
              type="button"
              onClick={handleRestart}
            >
              Réessayer
            </button>

            <button
              type="button"
              onClick={onOpenLesson}
            >
              Retour à la lecture
            </button>
          </div>
        </div>
      </section>
    )
  }

  if (questions.length === 0) {
    return (
      <section className="quiz-page">


        <header className="quiz-page__header">
          <div>
            <span className="quiz-page__slug">
              {moduleSlug}
            </span>

            <h1>
              Quiz — {module.titre}
            </h1>

            <p>
              Vérifiez vos connaissances
              avant de passer aux challenges.
            </p>
          </div>

          <button
            type="button"
            className="quiz-page__back"
            onClick={onBack}
          >
            ← Retour aux modules
          </button>
        </header>

        <div className="quiz-page__tabs">
          <button
            type="button"
            onClick={onOpenLesson}
          >
            📖 Lecture
          </button>

          <button
            type="button"
            className="is-active"
          >
            ❓ Quiz
          </button>

          <button
            type="button"
            onClick={onOpenChallenge}
          >
            🏆 Challenges
          </button>
        </div>

        <div className="quiz-page__empty">
          <span aria-hidden="true">
            ❓
          </span>

          <h2>Aucune question disponible</h2>

          <p>
            Ce quiz ne contient encore aucune
            question de la part du serveur.
          </p>

          <div className="quiz-page__empty-actions">
            <button
              type="button"
              onClick={onOpenLesson}
            >
              Retour à la lecture
            </button>

            <button
              type="button"
              className="is-challenge"
              onClick={onOpenChallenge}
            >
              Voir les challenges
            </button>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="quiz-page">


      <header className="quiz-page__header">
        <div>


          <h1>
            Quiz — {module.titre}
          </h1>

          <p>
            Répondez à toutes les questions
            pour valider cette étape du
            module.
          </p>
        </div>

        <button
          type="button"
          className="quiz-page__back"
          onClick={onBack}
        >
          ← Retour aux modules
        </button>
      </header>

      <div className="quiz-page__tabs">
        <button
          type="button"
          onClick={onOpenLesson}
        >
          📖 Lecture
        </button>

        <button
          type="button"
          className="is-active"
        >
          ❓ Quiz
        </button>

        <button
          type="button"
          onClick={onOpenChallenge}
        >
          🏆 Challenges
        </button>
      </div>

      <div className="quiz-page__layout">
        <main className="quiz-page__main">
          <div className="quiz-page__progress-card">
            <div className="quiz-page__progress-info">
              <span>
                Question{' '}
                {activeQuestionIndex + 1}
                {' sur '}
                {questions.length}
              </span>

              <strong>
                {progress}% complété
              </strong>
            </div>

            <div className="quiz-page__progress-track">
              <div
                className="quiz-page__progress-fill"
                style={{
                  width: `${progress}%`,
                }}
              />
            </div>
          </div>

          <article className="quiz-page__question">
            <div className="quiz-page__question-top">
              <span className="quiz-page__question-number">
                {activeQuestionIndex + 1}
              </span>

              <span className="quiz-page__question-type">
                {isCurrentShortAnswer
                  ? 'Réponse courte'
                  : isMultipleQuestion(
                        currentQuestion
                      )
                    ? 'Plusieurs réponses'
                    : 'Une seule réponse'}
              </span>
            </div>

            <h2>
              {getQuestionText(
                currentQuestion,
                activeQuestionIndex
              )}
            </h2>

            {isCurrentShortAnswer ? (
              <div className="quiz-page__short-answer">
                <textarea
                  rows={3}
                  disabled={
                    isFinished ||
                    isSavingCurrent
                  }
                  value={
                    shortAnswerDrafts[
                      currentQuestionId
                    ] ?? ''
                  }
                  onChange={(event) =>
                    handleShortAnswerChange(
                      currentQuestion,
                      activeQuestionIndex,
                      event.target.value
                    )
                  }
                  placeholder="Votre réponse…"
                />

                <button
                  type="button"
                  disabled={
                    isFinished ||
                    isSavingCurrent ||
                    !(
                      shortAnswerDrafts[
                        currentQuestionId
                      ] || ''
                    ).trim()
                  }
                  onClick={() =>
                    handleShortAnswerSubmit(
                      currentQuestion,
                      activeQuestionIndex
                    )
                  }
                >
                  {isSavingCurrent
                    ? 'Enregistrement…'
                    : 'Valider la réponse'}
                </button>
              </div>
            ) : currentOptions.length > 0 ? (
              <div className="quiz-page__options">
                {currentOptions.map(
                  (
                    option,
                    optionIndex
                  ) => {
                    const optionId =
                      getOptionId(
                        option,
                        optionIndex
                      )

                    const isSelected =
                      currentAnswers.includes(
                        optionId
                      )

                    const inputType =
                      isMultipleQuestion(
                        currentQuestion
                      )
                        ? 'checkbox'
                        : 'radio'

                    return (
                      <label
                        key={optionId}
                        className={[
                          'quiz-page__option',
                          isSelected
                            ? 'is-selected'
                            : '',
                        ]
                          .filter(Boolean)
                          .join(' ')}
                      >
                        <input
                          type={inputType}
                          name={`question-${currentQuestionId}`}
                          value={optionId}
                          checked={isSelected}
                          disabled={
                            isFinished ||
                            isSavingCurrent
                          }
                          onChange={() =>
                            handleSelectOption(
                              currentQuestion,
                              activeQuestionIndex,
                              option,
                              optionIndex
                            )
                          }
                        />

                        <span className="quiz-page__option-control" />

                        <span className="quiz-page__option-letter">
                          {String.fromCharCode(
                            65 + optionIndex
                          )}
                        </span>

                        <span className="quiz-page__option-text">
                          {getOptionText(
                            option,
                            optionIndex
                          )}
                        </span>
                      </label>
                    )
                  }
                )}
              </div>
            ) : (
              <div className="quiz-page__question-error">
                Cette question ne contient
                aucune réponse disponible.
              </div>
            )}

            {currentResult ? (
              <div
                className={[
                  'quiz-page__feedback',
                  currentResult.estCorrecte
                    ? 'is-correct'
                    : 'is-incorrect',
                ].join(' ')}
              >
                <strong>
                  {currentResult.estCorrecte
                    ? '✅ Bonne réponse'
                    : '❌ Réponse incorrecte'}
                </strong>

                {!currentResult.estCorrecte && (
                  <>
                    {formatCorrectionAnswer(
                      currentResult.correction,
                      currentOptions
                    ) && (
                      <p className="quiz-page__feedback-answer">
                        Bonne réponse :{' '}
                        <strong>
                          {formatCorrectionAnswer(
                            currentResult.correction,
                            currentOptions
                          )}
                        </strong>
                      </p>
                    )}

                    {currentResult.explication && (
                      <p>
                        {
                          currentResult.explication
                        }
                      </p>
                    )}
                  </>
                )}
              </div>
            ) : (
              isFinished &&
              getQuestionExplanation(
                currentQuestion
              ) && (
                <div className="quiz-page__explanation">
                  <strong>Explication</strong>

                  <p>
                    {getQuestionExplanation(
                      currentQuestion
                    )}
                  </p>
                </div>
              )
            )}
          </article>

          {saveError && (
            <div
              className="quiz-page__error"
              role="alert"
            >
              <span aria-hidden="true">
                ⚠️
              </span>

              <p>{saveError}</p>

              <button
                type="button"
                onClick={() =>
                  setSaveError('')
                }
                aria-label="Fermer le message"
              >
                ×
              </button>
            </div>
          )}

          <div className="quiz-page__navigation">
            <button
              type="button"
              className="quiz-page__previous"
              disabled={
                activeQuestionIndex === 0
              }
              onClick={
                handlePreviousQuestion
              }
            >
              ← Question précédente
            </button>

            {activeQuestionIndex <
            questions.length - 1 ? (
              <button
                type="button"
                className="quiz-page__next"
                disabled={
                  !isAnswerFilled(
                    answers[
                      currentQuestionId
                    ]
                  )
                }
                onClick={
                  handleNextQuestion
                }
              >
                Question suivante →
              </button>
            ) : (
              <button
                type="button"
                className="quiz-page__next"
                disabled={
                  !allAnswersCompleted ||
                  isFinished ||
                  isSubmitting ||
                  Object.values(savingQuestionIds).some(Boolean)
                }
                onClick={handleSubmitAttempt}
              >
                {isFinished
                  ? '✓ Quiz soumis'
                  : isSubmitting
                    ? 'Soumission…'
                    : allAnswersCompleted
                      ? 'Soumettre le quiz →'
                      : 'Répondez à toutes les questions'}
              </button>
            )}
          </div>

          {isFinished && scoreSummary && (
            <div
              className={[
                'quiz-page__result-summary',
                isSuccess
                  ? 'is-success'
                  : 'is-failure',
              ].join(' ')}
            >
              <div>
                <strong>
                  {isSuccess
                    ? '✓ Quiz réussi'
                    : 'Quiz non réussi'}
                </strong>
                <span>
                  {scoreSummary.percentage}% ·{' '}
                  {scoreSummary.correct} bonne(s) réponse(s) ·{' '}
                  {scoreSummary.incorrect} mauvaise(s)
                </span>
              </div>

              <button
                type="button"
                onClick={() => setShowResultModal(true)}
              >
                Voir le résultat
              </button>
            </div>
          )}
        </main>

        <aside className="quiz-page__sidebar">
          <div className="quiz-page__sidebar-card">
            <h3>Questions</h3>

            <p>
              {answeredQuestionsCount}
              {' sur '}
              {questions.length}
              {' réponses'}
            </p>

            <div className="quiz-page__question-list">
              {questions.map(
                (
                  question,
                  questionIndex
                ) => {
                  const questionId =
                    getQuestionId(
                      question,
                      questionIndex
                    )

                  const isAnswered =
                    isAnswerFilled(
                      answers[questionId]
                    )

                  const result =
                    questionResults[questionId]

                  const hasCorrection =
                    typeof result?.estCorrecte ===
                    'boolean'

                  const isActive =
                    activeQuestionIndex ===
                    questionIndex

                  return (
                    <button
                      key={questionId}
                      type="button"
                      className={[
                        isActive
                          ? 'is-active'
                          : '',
                        hasCorrection &&
                        result.estCorrecte
                          ? 'is-correct'
                          : '',
                        hasCorrection &&
                        !result.estCorrecte
                          ? 'is-incorrect'
                          : '',
                        isAnswered &&
                        !hasCorrection
                          ? 'is-answered'
                          : '',
                      ]
                        .filter(Boolean)
                        .join(' ')}
                      onClick={() =>
                        handleSelectQuestion(
                          questionIndex
                        )
                      }
                      aria-label={`Aller à la question ${questionIndex + 1}`}
                    >
                      {questionIndex + 1}
                    </button>
                  )
                }
              )}
            </div>
          </div>

          <div className="quiz-page__sidebar-card quiz-page__history-card">
            <h3>Mes tentatives</h3>

            {attempts.length > 0 ? (
              <div className="quiz-page__history-list">
                {attempts.slice(0, 3).map((attempt, index) => (
                  <div key={attempt?.id || index}>
                    <span>Tentative {attempts.length - index}</span>
                    <strong>{Number(attempt?.score || 0)}%</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p>Aucune tentative soumise.</p>
            )}
          </div>

          <div className="quiz-page__sidebar-card quiz-page__ranking-card">
            <h3>Classement</h3>

            {ranking.length > 0 ? (
              <div className="quiz-page__history-list">
                {ranking.slice(0, 3).map((entry) => (
                  <div key={`${entry.rang}-${entry.utilisateur_id}`}>
                    <span>#{entry.rang} {entry.utilisateur_nom}</span>
                    <strong>{entry.meilleur_score}%</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p>Classement encore vide.</p>
            )}

            {sideDataError && <small>{sideDataError}</small>}
          </div>

          <div className="quiz-page__sidebar-card quiz-page__sidebar-card--help">
            <span aria-hidden="true">
              💡
            </span>

            <h3>Conseil</h3>

            <p>
              Relisez attentivement chaque
              question avant de sélectionner
              votre réponse.
            </p>

            <button
              type="button"
              onClick={onOpenLesson}
            >
              Revoir la leçon
            </button>
          </div>
        </aside>
      </div>

      {resultModal}
    </section>
  )
}

export default Quiz
