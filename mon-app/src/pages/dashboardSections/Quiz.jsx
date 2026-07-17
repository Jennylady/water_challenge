import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'

import { getApiErrorMessage } from '../../api/api'
import { formationApi } from '../../api/services'

import './Quiz.css'

/* =========================================================
   UTILITAIRES
   ========================================================= */

const getModuleSlug = (module) =>
  String(module?.slug || '').trim()

const normalizeText = (value) =>
  String(value || '')
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')

const getQuestionId = (question, questionIndex) =>
  String(
    question?.id ??
      question?.uuid ??
      question?.ordre ??
      questionIndex
  )

const getQuestionText = (question, questionIndex) =>
  question?.texte ||
  question?.question ||
  question?.libelle ||
  question?.titre ||
  `Question ${questionIndex + 1}`

const getQuestionOptions = (question) => {
  const options =
    question?.choix ??
    question?.options ??
    question?.reponses ??
    question?.answers ??
    []

  if (Array.isArray(options)) {
    return options
  }

  if (options && typeof options === 'object') {
    return Object.entries(options).map(([key, value]) => {
      if (value && typeof value === 'object') {
        return {
          id: value.id ?? key,
          ...value,
        }
      }

      return {
        id: key,
        texte: String(value),
      }
    })
  }

  return []
}

const getOptionId = (option, optionIndex) => {
  if (option === null || option === undefined) {
    return String(optionIndex)
  }

  if (typeof option === 'string' || typeof option === 'number') {
    return String(optionIndex)
  }

  return String(
    option?.id ??
      option?.uuid ??
      option?.value ??
      option?.code ??
      optionIndex
  )
}

const getOptionText = (option, optionIndex) => {
  if (typeof option === 'string' || typeof option === 'number') {
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
  normalizeText(
    question?.type ||
      question?.type_question ||
      question?.question_type ||
      question?.format ||
      ''
  )

const isTextQuestion = (question) => {
  const questionType = getQuestionType(question)

  return (
    questionType.includes('texte') ||
    questionType.includes('text') ||
    questionType.includes('ouverte') ||
    questionType.includes('open') ||
    questionType.includes('libre') ||
    getQuestionOptions(question).length === 0
  )
}

const isMultipleQuestion = (question) => {
  const questionType = getQuestionType(question)

  return Boolean(
    question?.multiple ||
      question?.plusieurs_reponses ||
      question?.choix_multiple ||
      questionType === 'choix_multiple' ||
      questionType === 'multiple' ||
      questionType === 'multiple_choice' ||
      questionType === 'checkbox'
  )
}

const normalizeChoiceIds = (value) => {
  if (!value) {
    return []
  }

  if (Array.isArray(value)) {
    return value.map(String).filter(Boolean)
  }

  return [String(value)]
}

const createEmptyAnswer = () => ({
  choix_ids: [],
  reponse_texte: '',
})

const extractExistingAnswer = (question) => {
  const receivedAnswer =
    question?.reponse_utilisateur ??
    question?.reponse ??
    question?.derniere_reponse ??
    question?.user_answer ??
    {}

  const choiceIds =
    receivedAnswer?.choix_ids ??
    receivedAnswer?.choix_selectionnes ??
    question?.choix_ids ??
    question?.choix_selectionnes ??
    []

  const textAnswer =
    receivedAnswer?.reponse_texte ??
    receivedAnswer?.texte ??
    question?.reponse_texte ??
    ''

  return {
    choix_ids: normalizeChoiceIds(choiceIds),
    reponse_texte: String(textAnswer || ''),
  }
}

const getAnswerSignature = (answer) => {
  const choiceIds = [...(answer?.choix_ids || [])]
    .map(String)
    .sort()

  return JSON.stringify({
    choix_ids: choiceIds,
    reponse_texte: String(answer?.reponse_texte || '').trim(),
  })
}

const isQuestionAnswered = (question, answer) => {
  if (isTextQuestion(question)) {
    return Boolean(String(answer?.reponse_texte || '').trim())
  }

  return (
    Array.isArray(answer?.choix_ids) &&
    answer.choix_ids.length > 0
  )
}

/*
 * Extrait les ids des bonnes réponses depuis le feedback retourné par le
 * backend (answerQuestion / submitAttempt). Plusieurs noms de champs sont
 * tolérés car le format exact dépend de l’API.
 */
const getCorrectChoiceIds = (feedback) => {
  const correctIds =
    feedback?.choix_corrects_ids ??
    feedback?.choix_correct_ids ??
    feedback?.bonnes_reponses_ids ??
    feedback?.reponse_correcte_ids ??
    feedback?.correct_choix_ids ??
    feedback?.reponse_attendue_ids ??
    []

  return normalizeChoiceIds(correctIds)
}

/*
 * Idem pour une question à réponse libre (texte).
 */
const getCorrectAnswerText = (feedback) =>
  String(
    feedback?.reponse_correcte_texte ||
      feedback?.reponse_correcte ||
      feedback?.reponse_attendue ||
      feedback?.bonne_reponse ||
      feedback?.correction ||
      ''
  ).trim()

/* =========================================================
   COMPOSANT
   ========================================================= */

function Quiz({
  module,
  onBack,
  onOpenLesson,
  onOpenChallenge,
  onQuizSubmitted,
}) {
  const [quiz, setQuiz] = useState(null)
  const [questions, setQuestions] = useState([])
  const [tentativeId, setTentativeId] = useState('')

  const [answers, setAnswers] = useState({})
  const [savedAnswerSignatures, setSavedAnswerSignatures] = useState({})
  const [questionFeedback, setQuestionFeedback] = useState({})

  const [activeQuestionIndex, setActiveQuestionIndex] = useState(0)

  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [actionError, setActionError] = useState('')

  const [savingQuestionId, setSavingQuestionId] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [submittedTentative, setSubmittedTentative] = useState(null)

  const moduleSlug = getModuleSlug(module)

  /* =======================================================
     CHARGEMENT DU QUIZ ET DE LA TENTATIVE
     ======================================================= */

  const loadQuiz = useCallback(async () => {
    if (!moduleSlug) {
      setLoadError('Impossible d’identifier le module.')
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    setLoadError('')
    setActionError('')
    setIsSubmitted(false)
    setSubmittedTentative(null)
    setQuestionFeedback({})
    setActiveQuestionIndex(0)

    try {
      const receivedQuiz = await formationApi.getQuiz(moduleSlug)

      if (!receivedQuiz?.id) {
        throw new Error('Le serveur ne retourne pas un quiz valide.')
      }

      const receivedTentativeId = String(receivedQuiz?.tentative_id || '')

      if (!receivedTentativeId) {
        throw new Error(
          'Aucune tentative active n’a été créée pour ce quiz.'
        )
      }

      const receivedQuestions = Array.isArray(receivedQuiz.questions)
        ? receivedQuiz.questions
        : []

      const nextAnswers = {}
      const nextSavedSignatures = {}

      receivedQuestions.forEach((question, questionIndex) => {
        const questionId = getQuestionId(question, questionIndex)
        const existingAnswer = extractExistingAnswer(question)

        nextAnswers[questionId] = existingAnswer

        if (isQuestionAnswered(question, existingAnswer)) {
          nextSavedSignatures[questionId] =
            getAnswerSignature(existingAnswer)
        }
      })

      setQuiz(receivedQuiz)
      setTentativeId(receivedTentativeId)
      setQuestions(receivedQuestions)
      setAnswers(nextAnswers)
      setSavedAnswerSignatures(nextSavedSignatures)
    } catch (requestError) {
      console.error('Erreur de chargement du quiz :', requestError)

      setQuiz(null)
      setQuestions([])
      setTentativeId('')
      setAnswers({})
      setSavedAnswerSignatures({})

      setLoadError(
        getApiErrorMessage(
          requestError,
          'Impossible de charger le quiz.'
        )
      )
    } finally {
      setIsLoading(false)
    }
  }, [moduleSlug])

  useEffect(() => {
    loadQuiz()
  }, [loadQuiz])

  /* =======================================================
     QUESTION ACTIVE
     ======================================================= */

  const currentQuestion = questions[activeQuestionIndex]

  const currentQuestionId = currentQuestion
    ? getQuestionId(currentQuestion, activeQuestionIndex)
    : ''

  const currentOptions = currentQuestion
    ? getQuestionOptions(currentQuestion)
    : []

  const currentAnswer =
    answers[currentQuestionId] || createEmptyAnswer()

  const answeredQuestionsCount = useMemo(() => {
    return questions.filter((question, questionIndex) => {
      const questionId = getQuestionId(question, questionIndex)
      return isQuestionAnswered(question, answers[questionId])
    }).length
  }, [answers, questions])

  const progress =
    questions.length > 0
      ? Math.round((answeredQuestionsCount / questions.length) * 100)
      : 0

  /* =======================================================
     MODIFICATION D’UNE RÉPONSE
     ======================================================= */

  const handleSelectOption = (
    question,
    questionIndex,
    option,
    optionIndex
  ) => {
    if (isSubmitted || isSubmitting) {
      return
    }

    const questionId = getQuestionId(question, questionIndex)
    const optionId = getOptionId(option, optionIndex)
    const multiple = isMultipleQuestion(question)

    setAnswers((currentAnswersState) => {
      const previousAnswer =
        currentAnswersState[questionId] || createEmptyAnswer()

      const previousChoiceIds = previousAnswer.choix_ids || []

      if (!multiple) {
        return {
          ...currentAnswersState,
          [questionId]: {
            choix_ids: [optionId],
            reponse_texte: '',
          },
        }
      }

      const alreadySelected = previousChoiceIds.includes(optionId)

      const nextChoiceIds = alreadySelected
        ? previousChoiceIds.filter((currentId) => currentId !== optionId)
        : [...previousChoiceIds, optionId]

      return {
        ...currentAnswersState,
        [questionId]: {
          choix_ids: nextChoiceIds,
          reponse_texte: '',
        },
      }
    })

    setActionError('')
  }

  const handleTextAnswerChange = (question, questionIndex, value) => {
    if (isSubmitted || isSubmitting) {
      return
    }

    const questionId = getQuestionId(question, questionIndex)

    setAnswers((currentAnswersState) => ({
      ...currentAnswersState,
      [questionId]: {
        choix_ids: [],
        reponse_texte: value,
      },
    }))

    setActionError('')
  }

  /* =======================================================
     ENREGISTREMENT D’UNE RÉPONSE
     ======================================================= */

  const saveQuestionAnswer = useCallback(
    async (question, questionIndex, options = {}) => {
      const { force = false } = options

      if (!question) {
        return null
      }

      if (!tentativeId) {
        throw new Error('Aucune tentative active n’est disponible.')
      }

      const questionId = getQuestionId(question, questionIndex)
      const answer = answers[questionId] || createEmptyAnswer()

      if (!isQuestionAnswered(question, answer)) {
        throw new Error(
          `Veuillez répondre à la question ${questionIndex + 1}.`
        )
      }

      const currentSignature = getAnswerSignature(answer)
      const savedSignature = savedAnswerSignatures[questionId]

      if (!force && currentSignature === savedSignature) {
        return questionFeedback[questionId] || null
      }

      setSavingQuestionId(questionId)

      try {
        const payload = {
          choix_ids: isTextQuestion(question) ? [] : answer.choix_ids,
          reponse_texte: isTextQuestion(question)
            ? String(answer.reponse_texte || '').trim()
            : '',
        }

        const savedResponse = await formationApi.answerQuestion(
          tentativeId,
          questionId,
          payload
        )

        setSavedAnswerSignatures((currentSignatures) => ({
          ...currentSignatures,
          [questionId]: currentSignature,
        }))

        setQuestionFeedback((currentFeedback) => ({
          ...currentFeedback,
          [questionId]: savedResponse || {},
        }))

        return savedResponse
      } catch (requestError) {
        console.error(
          `Erreur pendant l’enregistrement de la question ${questionId} :`,
          requestError
        )

        throw new Error(
          getApiErrorMessage(
            requestError,
            'Impossible d’enregistrer cette réponse.'
          )
        )
      } finally {
        setSavingQuestionId('')
      }
    },
    [answers, questionFeedback, savedAnswerSignatures, tentativeId]
  )

  /* =======================================================
     NAVIGATION ENTRE LES QUESTIONS
     ======================================================= */

  const handlePreviousQuestion = () => {
    setActionError('')

    setActiveQuestionIndex((currentIndex) =>
      Math.max(currentIndex - 1, 0)
    )
  }

  /*
   * Vérifie la réponse à la question active : l’enregistre côté serveur
   * et affiche immédiatement si elle est correcte ou non, SANS avancer
   * à la question suivante et SANS soumettre la tentative.
   */
  const handleCheckAnswer = async () => {
    if (!currentQuestion) {
      return
    }

    setActionError('')

    try {
      await saveQuestionAnswer(currentQuestion, activeQuestionIndex)
    } catch (requestError) {
      setActionError(requestError.message)
    }
  }

  /*
   * Avance à la question suivante. Appelé seulement une fois que la
   * réponse actuelle a déjà été vérifiée (voir handleCheckAnswer).
   */
  const handleGoNext = () => {
    setActionError('')

    setActiveQuestionIndex((currentIndex) =>
      Math.min(currentIndex + 1, questions.length - 1)
    )

    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleSelectQuestion = (questionIndex) => {
    setActiveQuestionIndex(questionIndex)
    setActionError('')

    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  /* =======================================================
     SOUMISSION DE LA TENTATIVE
     ======================================================= */

  const handleSubmit = async () => {
    if (answeredQuestionsCount !== questions.length) {
      setActionError(
        'Veuillez répondre à toutes les questions avant de terminer le quiz.'
      )
      return
    }

    if (!tentativeId) {
      setActionError('Aucune tentative active n’est disponible.')
      return
    }

    setIsSubmitting(true)
    setActionError('')

    try {
      /*
       * Enregistre toutes les réponses qui ont été modifiées ou qui
       * ne sont pas encore sauvegardées.
       */
      for (
        let questionIndex = 0;
        questionIndex < questions.length;
        questionIndex += 1
      ) {
        await saveQuestionAnswer(questions[questionIndex], questionIndex)
      }

      /*
       * Le backend vérifie que toutes les questions ont une réponse,
       * recalcule le score et attribue les points.
       */
      const tentative = await formationApi.submitAttempt(tentativeId)

      if (!tentative?.id) {
        throw new Error(
          'Le serveur ne retourne pas le résultat de la tentative.'
        )
      }

      const submittedFeedback = {}

      if (Array.isArray(tentative.reponses)) {
        tentative.reponses.forEach((savedResponse) => {
          const questionId = String(savedResponse?.question_id || '')

          if (questionId) {
            submittedFeedback[questionId] = savedResponse
          }
        })
      }

      setQuestionFeedback((currentFeedback) => ({
        ...currentFeedback,
        ...submittedFeedback,
      }))

      setSubmittedTentative(tentative)
      setIsSubmitted(true)

      if (typeof onQuizSubmitted === 'function') {
        await onQuizSubmitted(tentative)
      }

      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (requestError) {
      console.error(
        'Erreur pendant la soumission du quiz :',
        requestError
      )

      setActionError(
        getApiErrorMessage(
          requestError,
          'Impossible de soumettre le quiz.'
        )
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  /* =======================================================
     NOUVELLE TENTATIVE
     ======================================================= */

  const handleRestart = async () => {
    /*
     * Après une soumission, le GET du quiz doit retourner ou créer
     * la tentative active suivante selon la logique backend.
     */
    await loadQuiz()

    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  /* =======================================================
     URL
     ======================================================= */

  const buildModuleUrl = (view = 'quiz') => {
    if (typeof window === 'undefined') {
      return '#'
    }

    const nextUrl = new URL(window.location.href)

    nextUrl.searchParams.set('section', 'learning')
    nextUrl.searchParams.set('module', moduleSlug)
    nextUrl.searchParams.set('view', view)
    nextUrl.searchParams.delete('moduleId')

    return nextUrl.pathname + nextUrl.search + nextUrl.hash
  }

  /* =======================================================
     MODULE ABSENT
     ======================================================= */

  if (!module) {
    return (
      <section className="quiz-page">
        <div className="quiz-page__empty">
          <span aria-hidden="true">⚠️</span>

          <h1>Module introuvable</h1>

          <p>
            Aucun module n’a été sélectionné pour afficher ce quiz.
          </p>

          {typeof onBack === 'function' && (
            <button type="button" onClick={onBack}>
              Retour aux modules
            </button>
          )}
        </div>
      </section>
    )
  }

  /* =======================================================
     CHARGEMENT
     ======================================================= */

  if (isLoading) {
    return (
      <section
        className="quiz-page"
        aria-busy="true"
        aria-live="polite"
      >
        <div className="quiz-page__empty">
          <span aria-hidden="true">⏳</span>

          <h2>Chargement du quiz</h2>

          <p>
            Préparation de votre tentative et des questions...
          </p>
        </div>
      </section>
    )
  }

  /* =======================================================
     ERREUR DE CHARGEMENT
     ======================================================= */

  if (loadError) {
    return (
      <section className="quiz-page">
        <nav className="quiz-page__breadcrumb" aria-label="Fil d’Ariane">
          <button type="button" onClick={onBack}>
            Formation
          </button>

          <span>/</span>

          <a href={buildModuleUrl()}>{moduleSlug}</a>

          <span>/</span>

          <strong>Quiz</strong>
        </nav>

        <div className="quiz-page__empty">
          <span aria-hidden="true">⚠️</span>

          <h2>Impossible de charger le quiz</h2>

          <p>{loadError}</p>

          <div className="quiz-page__empty-actions">
            <button type="button" onClick={loadQuiz}>
              Réessayer
            </button>

            <button
              type="button"
              className="is-challenge"
              onClick={onOpenLesson}
            >
              Retour à la lecture
            </button>
          </div>
        </div>
      </section>
    )
  }

  /* =======================================================
     AUCUNE QUESTION
     ======================================================= */

  if (questions.length === 0) {
    return (
      <section className="quiz-page">
        <nav className="quiz-page__breadcrumb" aria-label="Fil d’Ariane">
          <button type="button" onClick={onBack}>
            Formation
          </button>

          <span>/</span>

          <a href={buildModuleUrl()}>{moduleSlug}</a>

          <span>/</span>

          <strong>Quiz</strong>
        </nav>

        <header className="quiz-page__header">
          <div>
            <span className="quiz-page__slug">{moduleSlug}</span>

            <h1>{quiz?.titre || `Quiz — ${module.titre}`}</h1>

            <p>
              Vérifiez vos connaissances avant de passer aux
              challenges.
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

        <div className="quiz-page__empty">
          <span aria-hidden="true">❓</span>

          <h2>Aucune question disponible</h2>

          <p>
            Le serveur n’a retourné aucune question pour cette
            tentative.
          </p>

          <div className="quiz-page__empty-actions">
            <button type="button" onClick={loadQuiz}>
              Actualiser
            </button>

            <button
              type="button"
              className="is-challenge"
              onClick={onOpenLesson}
            >
              Retour à la lecture
            </button>
          </div>
        </div>
      </section>
    )
  }

  const currentFeedback = questionFeedback[currentQuestionId]

  const currentIsAnswered = isQuestionAnswered(
    currentQuestion,
    currentAnswer
  )

  const currentIsSaved =
    getAnswerSignature(currentAnswer) ===
    savedAnswerSignatures[currentQuestionId]

  /*
   * Une question est "vérifiée" dès que sa réponse actuelle a été
   * enregistrée et que le serveur a renvoyé un résultat (correct/faux),
   * indépendamment du fait que toute la tentative ait été soumise.
   */
  const currentHasFeedback =
    currentIsSaved &&
    Boolean(currentFeedback) &&
    typeof currentFeedback.est_correcte === 'boolean'

  const currentCorrectChoiceIds = currentHasFeedback
    ? getCorrectChoiceIds(currentFeedback)
    : []

  /* =======================================================
     AFFICHAGE DU QUIZ
     ======================================================= */

  return (
    <section className="quiz-page">

      <header className="quiz-page__header">
        <div>
          <span className="quiz-page__slug">{moduleSlug}</span>

          <h1>{quiz?.titre || `Quiz — ${module.titre}`}</h1>

          <p>
            Répondez à toutes les questions puis soumettez votre
            tentative pour obtenir votre score.
          </p>

          <div className="quiz-page__header-meta">
            <span>
              ❓ {quiz?.nombre_questions ?? questions.length} questions
            </span>

            <span>
              🎯 Score requis : {quiz?.score_de_reussite ?? 0}
            </span>

            <span>📝 Tentative en cours</span>
          </div>
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
        <button type="button" onClick={onOpenLesson}>
          📖 Lecture
        </button>

        <button type="button" className="is-active">
          ❓ Quiz
        </button>

        <button type="button" onClick={onOpenChallenge}>
          🏆 Challenges
        </button>
      </div>

      {isSubmitted && submittedTentative ? (
        <div className="quiz-page__result-only">
          <div
            className={[
              'quiz-page__result',
              submittedTentative.est_reussi ? 'is-success' : 'is-failed',
            ].join(' ')}
          >
            <span className="quiz-page__result-icon" aria-hidden="true">
              {submittedTentative.est_reussi ? '🎉' : '📘'}
            </span>

            <div className="quiz-page__result-content">
              <h3>
                {submittedTentative.est_reussi
                  ? 'Quiz réussi'
                  : 'Quiz terminé'}
              </h3>

              <p>
                Score : <strong>{submittedTentative.score}</strong>
              </p>

              <p>
                Réponses :{' '}
                <strong>
                  {submittedTentative.nombre_reponses}/
                  {submittedTentative.nombre_questions}
                </strong>
              </p>

              <p>
                Points obtenus :{' '}
                <strong>
                  {submittedTentative.points_obtenus}/
                  {submittedTentative.points_total}
                </strong>
              </p>
            </div>

            <div className="quiz-page__result-actions">
              <button type="button" onClick={handleRestart}>
                Refaire le quiz
              </button>

              <button
                type="button"
                className="is-challenge"
                onClick={onOpenChallenge}
              >
                Continuer vers les challenges →
              </button>
            </div>
          </div>
        </div>
      ) : (
      <div className="quiz-page__layout">
        <main className="quiz-page__main">
          <div className="quiz-page__progress-card">
            <div className="quiz-page__progress-info">
              <span>
                Question {activeQuestionIndex + 1}
                {' sur '}
                {questions.length}
              </span>

              <strong>{progress}% complété</strong>
            </div>

            <div className="quiz-page__progress-track">
              <div
                className="quiz-page__progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          <article className="quiz-page__question">
            

            <h2>
              {getQuestionText(currentQuestion, activeQuestionIndex)}
            </h2>

            {isTextQuestion(currentQuestion) ? (
              <div className="quiz-page__text-answer">
                <label htmlFor={`question-${currentQuestionId}`}>
                  Votre réponse
                </label>

                <textarea
                  id={`question-${currentQuestionId}`}
                  value={currentAnswer.reponse_texte}
                  rows={6}
                  disabled={
                    isSubmitted || isSubmitting || currentHasFeedback
                  }
                  placeholder="Saisissez votre réponse ici..."
                  onChange={(event) =>
                    handleTextAnswerChange(
                      currentQuestion,
                      activeQuestionIndex,
                      event.target.value
                    )
                  }
                />
              </div>
            ) : (
              <div className="quiz-page__options">
                {currentOptions.map((option, optionIndex) => {
                  const optionId = getOptionId(option, optionIndex)

                  const isSelected =
                    currentAnswer.choix_ids.includes(optionId)

                  const isCorrectOption =
                    currentCorrectChoiceIds.includes(optionId)

                  const inputType = isMultipleQuestion(currentQuestion)
                    ? 'checkbox'
                    : 'radio'

                  const feedbackClass = currentHasFeedback
                    ? isSelected
                      ? currentFeedback?.est_correcte === true
                        ? 'is-correct'
                        : currentFeedback?.est_correcte === false
                          ? 'is-wrong'
                          : ''
                      : isCorrectOption
                        ? 'is-correct-answer'
                        : ''
                    : ''

                  return (
                    <label
                      key={optionId}
                      className={[
                        'quiz-page__option',
                        isSelected ? 'is-selected' : '',
                        feedbackClass,
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
                          isSubmitted ||
                          isSubmitting ||
                          currentHasFeedback
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
                        {String.fromCharCode(65 + optionIndex)}
                      </span>

                      <span className="quiz-page__option-text">
                        {getOptionText(option, optionIndex)}
                      </span>

                      {currentHasFeedback && isCorrectOption && !isSelected && (
                        <span className="quiz-page__option-tag">
                          Bonne réponse
                        </span>
                      )}
                    </label>
                  )
                })}
              </div>
            )}

            {/* {!isSubmitted && (
              <div className="quiz-page__save-status">
                {savingQuestionId === currentQuestionId ? (
                  <span className="is-saving">⏳ Enregistrement...</span>
                ) : currentIsSaved && currentIsAnswered ? (
                  <span className="is-saved">✓ Réponse enregistrée</span>
                ) : currentIsAnswered ? (
                  <span className="is-pending">
                    • Réponse non enregistrée
                  </span>
                ) : (
                  <span>
                    Sélectionnez ou écrivez une réponse.
                  </span>
                )}
              </div>
            )} */}

            {currentHasFeedback && (
              <div
                className={[
                  'quiz-page__explanation',
                  currentFeedback.est_correcte === true
                    ? 'is-correct'
                    : 'is-wrong',
                ].join(' ')}
              >
                <strong>
                  {currentFeedback.est_correcte === true
                    ? '✓ Bonne réponse'
                    : '✕ Réponse incorrecte'}
                </strong>

                {currentFeedback.explication && (
                  <p>{currentFeedback.explication}</p>
                )}

                {currentFeedback.est_correcte === false &&
                  isTextQuestion(currentQuestion) &&
                  getCorrectAnswerText(currentFeedback) && (
                    <p className="quiz-page__correction">
                      <strong>Réponse attendue :</strong>{' '}
                      {getCorrectAnswerText(currentFeedback)}
                    </p>
                  )}
              </div>
            )}
          </article>

          {actionError && (
            <div className="quiz-page__error" role="alert">
              <span aria-hidden="true">⚠️</span>

              <p>{actionError}</p>

              <button
                type="button"
                onClick={() => setActionError('')}
                aria-label="Fermer"
              >
                ×
              </button>
            </div>
          )}

          {!isSubmitted && (
            <div className="quiz-page__navigation">
              <button
                type="button"
                className="quiz-page__previous"
                disabled={
                  activeQuestionIndex === 0 ||
                  isSubmitting ||
                  Boolean(savingQuestionId)
                }
                onClick={handlePreviousQuestion}
              >
                ← Question précédente
              </button>

              {!currentHasFeedback ? (
                <button
                  type="button"
                  className="quiz-page__next"
                  disabled={
                    !currentIsAnswered ||
                    isSubmitting ||
                    Boolean(savingQuestionId)
                  }
                  onClick={handleCheckAnswer}
                >
                  {savingQuestionId
                    ? 'Vérification...'
                    : 'Vérifier la réponse'}
                </button>
              ) : activeQuestionIndex < questions.length - 1 ? (
                <button
                  type="button"
                  className="quiz-page__next"
                  disabled={isSubmitting || Boolean(savingQuestionId)}
                  onClick={handleGoNext}
                >
                  Question suivante →
                </button>
              ) : (
                <button
                  type="button"
                  className="quiz-page__submit"
                  disabled={
                    answeredQuestionsCount !== questions.length ||
                    isSubmitting ||
                    Boolean(savingQuestionId)
                  }
                  onClick={handleSubmit}
                >
                  {isSubmitting
                    ? 'Notation en cours...'
                    : 'Soumettre le quiz'}
                </button>
              )}
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
              {questions.map((question, questionIndex) => {
                const questionId = getQuestionId(
                  question,
                  questionIndex
                )

                const questionAnswer = answers[questionId]

                const answered = isQuestionAnswered(
                  question,
                  questionAnswer
                )

                const saved =
                  answered &&
                  getAnswerSignature(questionAnswer) ===
                    savedAnswerSignatures[questionId]

             
                const feedback = questionFeedback[questionId]

                const hasCorrection =
                  typeof feedback?.est_correcte === 'boolean'

                const active = questionIndex === activeQuestionIndex

                return (
                  <button
                    key={questionId}
                    type="button"
                    className={[
                      active ? 'is-active' : '',
                      hasCorrection && feedback.est_correcte
                        ? 'is-correct'
                        : '',
                      hasCorrection && !feedback.est_correcte
                        ? 'is-incorrect'
                        : '',
                      !hasCorrection && answered ? 'is-answered' : '',
                      !hasCorrection && saved ? 'is-saved' : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    onClick={() => handleSelectQuestion(questionIndex)}
                    aria-label={`Aller à la question ${questionIndex + 1}`}
                  >
                    {questionIndex + 1}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="quiz-page__sidebar-card quiz-page__sidebar-card--help">
            <span aria-hidden="true">💡</span>

            <h3>Conseil</h3>

            <p>
              Chaque réponse est enregistrée lorsque vous cliquez sur
              « Enregistrer et continuer ».
            </p>

            <button type="button" onClick={onOpenLesson}>
              Revoir la leçon
            </button>
          </div>
        </aside>
      </div>
      )}
    </section>
  )
}

export default Quiz