import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import './Quiz.css'

const getModuleSlug = (module) =>
  String(
    module?.slug ||
      module?.id ||
      'module'
  )

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

const isMultipleQuestion = (question) => {
  const questionType = String(
    question?.type ||
      question?.question_type ||
      ''
  ).toLowerCase()

  return Boolean(
    question?.multiple ||
      question?.plusieurs_reponses ||
      question?.choix_multiple ||
      questionType === 'multiple' ||
      questionType === 'checkbox'
  )
}

const getCorrectOptionIds = (question) => {
  const directCorrectAnswers =
    question?.bonnes_reponses ??
    question?.reponses_correctes ??
    question?.correct_answers ??
    question?.correct_option_ids ??
    question?.bonne_reponse ??
    question?.reponse_correcte ??
    question?.correct_answer

  if (
    directCorrectAnswers !== undefined &&
    directCorrectAnswers !== null
  ) {
    const values = Array.isArray(
      directCorrectAnswers
    )
      ? directCorrectAnswers
      : [directCorrectAnswers]

    return values.map(String)
  }

  return getQuestionOptions(question)
    .map((option, optionIndex) => ({
      id: getOptionId(
        option,
        optionIndex
      ),
      isCorrect: Boolean(
        option?.est_correcte ??
          option?.est_correct ??
          option?.is_correct ??
          option?.correct
      ),
    }))
    .filter((option) => option.isCorrect)
    .map((option) => option.id)
}

const areAnswersEqual = (
  firstAnswers,
  secondAnswers
) => {
  const first = [...firstAnswers].sort()
  const second = [...secondAnswers].sort()

  if (first.length !== second.length) {
    return false
  }

  return first.every(
    (answer, index) =>
      answer === second[index]
  )
}

function Quiz({
  module,
  questions: receivedQuestions,
  onBack,
  onOpenLesson,
  onOpenChallenge,
  onSubmit,
}) {
  const questions = useMemo(() => {
    if (
      Array.isArray(receivedQuestions)
    ) {
      return receivedQuestions
    }

    const moduleQuestions =
      module?.quiz?.questions ??
      module?.questions ??
      module?.quiz_questions ??
      []

    return Array.isArray(moduleQuestions)
      ? moduleQuestions
      : []
  }, [module, receivedQuestions])

  const [activeQuestionIndex, setActiveQuestionIndex] =
    useState(0)

  const [answers, setAnswers] =
    useState({})

  const [isSubmitted, setIsSubmitted] =
    useState(false)

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [submitError, setSubmitError] =
    useState('')

  useEffect(() => {
    setActiveQuestionIndex(0)
    setAnswers({})
    setIsSubmitted(false)
    setIsSubmitting(false)
    setSubmitError('')
  }, [module?.id])

  const moduleSlug =
    getModuleSlug(module)

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
      ? getQuestionOptions(
          currentQuestion
        )
      : []

  const currentAnswers =
    answers[currentQuestionId] || []

  const answeredQuestionsCount =
    useMemo(() => {
      return questions.filter(
        (question, questionIndex) => {
          const questionId =
            getQuestionId(
              question,
              questionIndex
            )

          return (
            answers[questionId]?.length >
            0
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

  const quizResult = useMemo(() => {
    let correctAnswers = 0
    let correctedQuestions = 0

    questions.forEach(
      (question, questionIndex) => {
        const correctOptionIds =
          getCorrectOptionIds(question)

        if (
          correctOptionIds.length === 0
        ) {
          return
        }

        correctedQuestions += 1

        const questionId =
          getQuestionId(
            question,
            questionIndex
          )

        const selectedAnswers =
          answers[questionId] || []

        if (
          areAnswersEqual(
            selectedAnswers,
            correctOptionIds
          )
        ) {
          correctAnswers += 1
        }
      }
    )

    return {
      correctAnswers,
      correctedQuestions,
      percentage:
        correctedQuestions > 0
          ? Math.round(
              (correctAnswers /
                correctedQuestions) *
                100
            )
          : null,
    }
  }, [answers, questions])

  const buildModuleUrl = (
    view = 'quiz'
  ) => {
    if (
      typeof window === 'undefined'
    ) {
      return '#'
    }

    const nextUrl = new URL(
      window.location.href
    )

    nextUrl.searchParams.set(
      'section',
      'learning'
    )

    nextUrl.searchParams.set(
      'module',
      moduleSlug
    )

    nextUrl.searchParams.set(
      'view',
      view
    )

    nextUrl.searchParams.delete(
      'moduleId'
    )

    return `${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}`
  }

  const handleSelectOption = (
    question,
    questionIndex,
    option,
    optionIndex
  ) => {
    if (isSubmitted) {
      return
    }

    const questionId =
      getQuestionId(
        question,
        questionIndex
      )

    const optionId =
      getOptionId(
        option,
        optionIndex
      )

    const multiple =
      isMultipleQuestion(question)

    setAnswers((currentAnswersState) => {
      const previousAnswers =
        currentAnswersState[questionId] ||
        []

      if (!multiple) {
        return {
          ...currentAnswersState,
          [questionId]: [optionId],
        }
      }

      const isAlreadySelected =
        previousAnswers.includes(optionId)

      const nextQuestionAnswers =
        isAlreadySelected
          ? previousAnswers.filter(
              (answerId) =>
                answerId !== optionId
            )
          : [
              ...previousAnswers,
              optionId,
            ]

      return {
        ...currentAnswersState,
        [questionId]:
          nextQuestionAnswers,
      }
    })
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
    setActiveQuestionIndex(0)
    setAnswers({})
    setIsSubmitted(false)
    setIsSubmitting(false)
    setSubmitError('')

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  const handleSubmit = async () => {
    if (
      answeredQuestionsCount !==
      questions.length
    ) {
      setSubmitError(
        'Veuillez répondre à toutes les questions avant de terminer le quiz.'
      )

      return
    }

    setIsSubmitting(true)
    setSubmitError('')

    const result = {
      moduleId: module?.id,
      moduleSlug,
      answers,
      totalQuestions:
        questions.length,
      correctAnswers:
        quizResult.correctAnswers,
      correctedQuestions:
        quizResult.correctedQuestions,
      percentage:
        quizResult.percentage,
    }

    try {
      if (
        typeof onSubmit === 'function'
      ) {
        await onSubmit(result)
      }

      setIsSubmitted(true)
    } catch (error) {
      console.error(
        "Erreur pendant l'envoi du quiz :",
        error
      )

      setSubmitError(
        error?.response?.data?.erreur ||
          error?.response?.data?.detail ||
          error?.response?.data?.message ||
          error?.message ||
          "Impossible d'envoyer le quiz."
      )
    } finally {
      setIsSubmitting(false)
    }
  }

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

  if (questions.length === 0) {
    return (
      <section className="quiz-page">
        <nav
          className="quiz-page__breadcrumb"
          aria-label="Fil d’Ariane"
        >
          <button
            type="button"
            onClick={onBack}
          >
            Formation
          </button>

          <span>/</span>

          <a
            href={buildModuleUrl('quiz')}
          >
            {moduleSlug}
          </a>

          <span>/</span>

          <strong>Quiz</strong>
        </nav>

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

          <h2>Quiz débloqué</h2>

          <p>
            Le quiz est disponible, mais
            aucune question n’a encore été
            transmise au composant.
          </p>

          <p>
            L’endpoint actuel du module
            retourne seulement le champ
            <strong>
              {' '}quiz_disponible
            </strong>
            . Les questions devront être
            récupérées depuis l’endpoint du
            quiz.
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
      <nav
        className="quiz-page__breadcrumb"
        aria-label="Fil d’Ariane"
      >
        <button
          type="button"
          onClick={onBack}
        >
          Formation
        </button>

        <span>/</span>

        <a href={buildModuleUrl('quiz')}>
          {moduleSlug}
        </a>

        <span>/</span>

        <strong>Quiz</strong>
      </nav>

      <header className="quiz-page__header">
        <div>
          <span className="quiz-page__slug">
            {moduleSlug}
          </span>

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
                {isMultipleQuestion(
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

            {currentOptions.length > 0 ? (
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
                            isSubmitted
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

            {isSubmitted &&
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
              )}
          </article>

          {submitError && (
            <div
              className="quiz-page__error"
              role="alert"
            >
              <span aria-hidden="true">
                ⚠️
              </span>

              <p>{submitError}</p>

              <button
                type="button"
                onClick={() =>
                  setSubmitError('')
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
                activeQuestionIndex === 0 ||
                isSubmitting
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
                  currentAnswers.length ===
                    0 ||
                  isSubmitting
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
                className="quiz-page__submit"
                disabled={
                  answeredQuestionsCount !==
                    questions.length ||
                  isSubmitted ||
                  isSubmitting
                }
                onClick={handleSubmit}
              >
                {isSubmitting
                  ? 'Envoi...'
                  : isSubmitted
                    ? 'Quiz terminé'
                    : 'Terminer le quiz'}
              </button>
            )}
          </div>

          {isSubmitted && (
            <div className="quiz-page__result">
              <span
                className="quiz-page__result-icon"
                aria-hidden="true"
              >
                🎉
              </span>

              <div className="quiz-page__result-content">
                <h3>Quiz terminé</h3>

                {quizResult.percentage !==
                null ? (
                  <p>
                    Vous avez obtenu{' '}
                    <strong>
                      {
                        quizResult.correctAnswers
                      }
                      /
                      {
                        quizResult.correctedQuestions
                      }
                    </strong>
                    , soit{' '}
                    <strong>
                      {
                        quizResult.percentage
                      }
                      %
                    </strong>
                    .
                  </p>
                ) : (
                  <p>
                    Toutes vos réponses ont
                    été enregistrées.
                  </p>
                )}
              </div>

              <div className="quiz-page__result-actions">
                <button
                  type="button"
                  onClick={handleRestart}
                >
                  Recommencer
                </button>

                <button
                  type="button"
                  className="is-challenge"
                  onClick={
                    onOpenChallenge
                  }
                >
                  Voir les challenges →
                </button>
              </div>
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
                    answers[questionId]
                      ?.length > 0

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
                        isAnswered
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
    </section>
  )
}

export default Quiz