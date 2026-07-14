import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import './Read.css'

const getModuleSlug = (module) =>
  String(
    module?.slug ||
      module?.id ||
      'module'
  )

const getLessonTitle = (
  lesson,
  lessonIndex
) =>
  lesson?.titre ||
  lesson?.title ||
  lesson?.nom ||
  `Leçon ${lessonIndex + 1}`

const getLessonContent = (lesson) =>
  lesson?.contenu ??
  lesson?.content ??
  lesson?.texte ??
  lesson?.description ??
  ''

const getLessonHtml = (lesson) =>
  lesson?.contenu_html ??
  lesson?.content_html ??
  lesson?.html ??
  ''

const getLessonIllustrations = (
  lesson,
  module
) => {
  const illustrations =
    lesson?.illustrations ??
    lesson?.images ??
    module?.illustrations ??
    []

  if (!Array.isArray(illustrations)) {
    return []
  }

  return [...illustrations].sort(
    (firstIllustration, secondIllustration) =>
      Number(
        firstIllustration?.ordre ?? 0
      ) -
      Number(
        secondIllustration?.ordre ?? 0
      )
  )
}


const getModuleLessons = (module) => {
  const receivedLessons =
    module?.lecons ??
    module?.lessons ??
    module?.chapitres ??
    module?.contenus ??
    []

  if (
    Array.isArray(receivedLessons) &&
    receivedLessons.length > 0
  ) {
    return [...receivedLessons].sort(
      (firstLesson, secondLesson) =>
        Number(firstLesson?.ordre ?? 0) -
        Number(secondLesson?.ordre ?? 0)
    )
  }

  const hasModuleContent = Boolean(
    module?.contenu ||
      module?.video ||
      (
        Array.isArray(
          module?.illustrations
        ) &&
        module.illustrations.length > 0
      )
  )

  if (!hasModuleContent) {
    return []
  }

  return [
    {
      id: `${module.id}-contenu`,
      titre:
        module.titre ||
        'Contenu du module',
      contenu: module.contenu || '',
      video: module.video || '',
      illustrations:
        module.illustrations || [],
      ordre: 1,
    },
  ]
}

const isHtmlContent = (content) => {
  if (typeof content !== 'string') {
    return false
  }

  return /<\/?[a-z][\s\S]*>/i.test(
    content
  )
}

function Read({
  module,
  getMediaUrl,
  onBack,
  onOpenQuiz,
  onOpenChallenge,
}) {
  const [activeLessonIndex, setActiveLessonIndex] =
    useState(0)

  const lessons = useMemo(
    () => getModuleLessons(module),
    [module]
  )

  useEffect(() => {
    setActiveLessonIndex(0)
  }, [module?.id])

  const moduleSlug =
    getModuleSlug(module)

  const safeLessonIndex = Math.min(
    activeLessonIndex,
    Math.max(lessons.length - 1, 0)
  )

  const activeLesson =
    lessons[safeLessonIndex]

  const lessonTitle =
    activeLesson
      ? getLessonTitle(
          activeLesson,
          safeLessonIndex
        )
      : ''

  const lessonContent =
    activeLesson
      ? getLessonContent(activeLesson)
      : ''

  const lessonHtml =
    activeLesson
      ? getLessonHtml(activeLesson)
      : ''

  const resolveMediaUrl = (mediaPath) => {
    if (!mediaPath) {
      return ''
    }

    if (
      typeof getMediaUrl === 'function'
    ) {
      return getMediaUrl(mediaPath)
    }

    return mediaPath
  }

  const moduleCover = resolveMediaUrl(
    module?.image_couverture
  )

  const lessonImage = resolveMediaUrl(
    activeLesson?.image ??
      activeLesson?.illustration ??
      ''
  )

  const lessonVideo = resolveMediaUrl(
    activeLesson?.video ??
      activeLesson?.video_url ??
      module?.video ??
      ''
  )

  const lessonDocument = resolveMediaUrl(
    activeLesson?.fichier ??
      activeLesson?.document ??
      activeLesson?.resource_url ??
      ''
  )

  const illustrations =
    getLessonIllustrations(
      activeLesson,
      module
    )

  const quizAvailable =
    module?.quiz_disponible !== false

  const updateUrl = (
    section,
    view = ''
  ) => {
    if (
      typeof window === 'undefined'
    ) {
      return
    }

    const nextUrl = new URL(
      window.location.href
    )

    nextUrl.searchParams.set(
      'section',
      section
    )

    if (moduleSlug) {
      nextUrl.searchParams.set(
        'module',
        moduleSlug
      )
    }

    nextUrl.searchParams.delete(
      'moduleId'
    )

    if (view) {
      nextUrl.searchParams.set(
        'view',
        view
      )
    } else {
      nextUrl.searchParams.delete(
        'view'
      )
    }

    window.history.pushState(
      {
        section,
        moduleSlug,
        moduleId: module?.id,
        view,
      },
      '',
      nextUrl
    )
  }

  const handleBack = () => {
    if (
      typeof window !== 'undefined'
    ) {
      const nextUrl = new URL(
        window.location.href
      )

      nextUrl.searchParams.set(
        'section',
        'learning'
      )

      nextUrl.searchParams.delete(
        'module'
      )

      nextUrl.searchParams.delete(
        'moduleId'
      )

      nextUrl.searchParams.delete(
        'view'
      )

      window.history.pushState(
        {
          section: 'learning',
        },
        '',
        nextUrl
      )
    }

    if (typeof onBack === 'function') {
      onBack()
    }
  }

  const handleOpenQuiz = () => {
    if (!quizAvailable) {
      return
    }

    updateUrl('learning', 'quiz')

    if (
      typeof onOpenQuiz === 'function'
    ) {
      onOpenQuiz(module)
    }
  }

  const handleOpenChallenge = () => {
    sessionStorage.setItem(
      'waterChallengeChallengeModuleId',
      String(module.id)
    )

    sessionStorage.setItem(
      'waterChallengeChallengeModuleSlug',
      moduleSlug
    )

    sessionStorage.setItem(
      'waterChallengeChallengeModule',
      JSON.stringify(module)
    )

    updateUrl('challenges')

    if (
      typeof onOpenChallenge ===
      'function'
    ) {
      onOpenChallenge(module)
    }
  }

  const handlePreviousLesson = () => {
    setActiveLessonIndex(
      (currentIndex) =>
        Math.max(currentIndex - 1, 0)
    )

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  const handleNextLesson = () => {
    setActiveLessonIndex(
      (currentIndex) =>
        Math.min(
          currentIndex + 1,
          lessons.length - 1
        )
    )

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  const handleSelectLesson = (
    lessonIndex
  ) => {
    setActiveLessonIndex(lessonIndex)

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  if (!module) {
    return (
      <section className="read-page">
        <div className="read-page__empty-state">
          <span aria-hidden="true">
            ⚠️
          </span>

          <h1>Module introuvable</h1>

          <p>
            Aucun module n’a été
            sélectionné pour la lecture.
          </p>

          {typeof onBack ===
            'function' && (
            <button
              type="button"
              onClick={handleBack}
            >
              Retour aux modules
            </button>
          )}
        </div>
      </section>
    )
  }

  return (
    <section className="read-page">
      
      <header className="read-page__header">
        <div className="read-page__header-content">
          <span className="read-page__slug">
            {moduleSlug}
          </span>

          <h1>
            {module.titre ||
              'Contenu du module'}
          </h1>

          <p>
            {module.resume ||
              'Consultez le contenu du module avant de passer au quiz et aux challenges.'}
          </p>

          <div className="read-page__header-meta">
            <span>
              📚 {lessons.length}{' '}
              {lessons.length > 1
                ? 'leçons'
                : 'leçon'}
            </span>

            <span>
              🎯{' '}
              {module.niveau ||
                'Débutant'}
            </span>

            {module.est_lu && (
              <span className="is-read">
                ✓ Module lu
              </span>
            )}
          </div>
        </div>

        <button
          type="button"
          className="read-page__back"
          onClick={handleBack}
        >
          ← Retour aux modules
        </button>
      </header>

      {/* <div className="read-page__tabs">
        <button
          type="button"
          className="is-active"
        >
          📖 Lecture
        </button>

        <button
          type="button"
          disabled={!quizAvailable}
          onClick={handleOpenQuiz}
        >
          ❓ Quiz
        </button>

        <button
          type="button"
          onClick={handleOpenChallenge}
        >
          🏆 Challenges
        </button>
      </div> */}

      {moduleCover && (
        <div className="read-page__cover">
          

          <div className="read-page__cover-overlay">
            <span>Water Challenge</span>

            <strong>
              {module.titre}
            </strong>
          </div>
        </div>
      )}

      <div className="read-page__layout">
        <aside className="read-page__sidebar">
          <div className="read-page__sidebar-header">
            <div>
              <span>Contenu</span>

              <strong>
                {lessons.length}{' '}
                {lessons.length > 1
                  ? 'leçons'
                  : 'leçon'}
              </strong>
            </div>
          </div>

          {lessons.length === 0 ? (
            <div className="read-page__sidebar-empty">
              Aucun contenu disponible.
            </div>
          ) : (
            <div className="read-page__lesson-list">
              {lessons.map(
                (
                  lesson,
                  lessonIndex
                ) => {
                  const isActive =
                    lessonIndex ===
                    safeLessonIndex

                  return (
                    <button
                      key={
                        lesson?.id ??
                        lessonIndex
                      }
                      type="button"
                      className={[
                        'read-page__lesson-button',
                        isActive
                          ? 'is-active'
                          : '',
                      ]
                        .filter(Boolean)
                        .join(' ')}
                      onClick={() =>
                        handleSelectLesson(
                          lessonIndex
                        )
                      }
                    >
                      <span className="read-page__lesson-number">
                        {lessonIndex + 1}
                      </span>

                      <span className="read-page__lesson-label">
                        <small>
                          Leçon{' '}
                          {lessonIndex + 1}
                        </small>

                        <strong>
                          {getLessonTitle(
                            lesson,
                            lessonIndex
                          )}
                        </strong>
                      </span>

                      <span
                        className="read-page__lesson-arrow"
                        aria-hidden="true"
                      >
                        ›
                      </span>
                    </button>
                  )
                }
              )}
            </div>
          )}

          <div className="read-page__sidebar-progress">
            <div>
              <span>Progression</span>

              <strong>
                {lessons.length > 0
                  ? Math.round(
                      (
                        (safeLessonIndex +
                          1) /
                        lessons.length
                      ) *
                        100
                    )
                  : 0}
                %
              </strong>
            </div>

            <div className="read-page__progress-track">
              <div
                className="read-page__progress-fill"
                style={{
                  width:
                    lessons.length > 0
                      ? `${Math.round(
                          (
                            (safeLessonIndex +
                              1) /
                            lessons.length
                          ) *
                            100
                        )}%`
                      : '0%',
                }}
              />
            </div>
          </div>
        </aside>

        <main className="read-page__main">
          {activeLesson ? (
            <article className="read-page__content-card">
              <div className="read-page__content-heading">
                <div>
                  <span>
                    Leçon{' '}
                    {safeLessonIndex + 1}
                    {' sur '}
                    {lessons.length}
                  </span>

                  {/* <h2>{lessonTitle}</h2> */}
                </div>

                {activeLesson.duree && (
                  <span className="read-page__duration">
                    ⏱{' '}
                    {activeLesson.duree}
                  </span>
                )}
              </div>

              {lessonImage && (
                <div className="read-page__lesson-image">
                  <img
                    src={lessonImage}
                    alt={lessonTitle}
                    onError={(event) => {
                      event.currentTarget.style.display =
                        'none'
                    }}
                  />
                </div>
              )}

              {lessonVideo && (
                <div className="read-page__video-section">
                 

                  <video
                    src={lessonVideo}
                    controls
                    preload="metadata"
                  >
                    Votre navigateur ne
                    prend pas en charge la
                    lecture de vidéos.
                  </video>
                </div>
              )}

              {lessonHtml ? (
                <div
                  className="read-page__lesson-content read-page__lesson-content--html"
                  dangerouslySetInnerHTML={{
                    __html: lessonHtml,
                  }}
                />
              ) : isHtmlContent(
                  lessonContent
                ) ? (
                <div
                  className="read-page__lesson-content read-page__lesson-content--html"
                  dangerouslySetInnerHTML={{
                    __html: lessonContent,
                  }}
                />
              ) : (
                <div className="read-page__lesson-content">
                  {lessonContent ? (
                    lessonContent
                      .split('\n')
                      .map(
                        (
                          paragraph,
                          paragraphIndex
                        ) => {
                          if (
                            !paragraph.trim()
                          ) {
                            return (
                              <br
                                key={
                                  paragraphIndex
                                }
                              />
                            )
                          }

                          return (
                            <p
                              key={
                                paragraphIndex
                              }
                            >
                              {paragraph}
                            </p>
                          )
                        }
                      )
                  ) : (
                    <p className="read-page__content-empty">
                      Aucun contenu textuel
                      n’est disponible pour
                      cette leçon.
                    </p>
                  )}
                </div>
              )}

              {illustrations.length > 0 && (
                <div className="read-page__illustrations">
                  <div className="read-page__section-title">
                    <span aria-hidden="true">
                      🖼️
                    </span>

                    <h3>Illustrations</h3>
                  </div>

                  <div className="read-page__illustration-grid">
                    {illustrations.map(
                      (
                        illustration,
                        illustrationIndex
                      ) => {
                        const imageUrl =
                          resolveMediaUrl(
                            illustration?.image ??
                              illustration?.url ??
                              illustration
                          )

                        if (!imageUrl) {
                          return null
                        }

                        return (
                          <figure
                            key={
                              illustration?.id ??
                              illustrationIndex
                            }
                          >
                            <img
                              src={imageUrl}
                              alt={
                                illustration?.legende ||
                                `Illustration ${illustrationIndex + 1}`
                              }
                              loading="lazy"
                              onError={(
                                event
                              ) => {
                                event.currentTarget.style.display =
                                  'none'
                              }}
                            />

                            {illustration?.legende && (
                              <figcaption>
                                {
                                  illustration.legende
                                }
                              </figcaption>
                            )}
                          </figure>
                        )
                      }
                    )}
                  </div>
                </div>
              )}

              {lessonDocument && (
                <a
                  className="read-page__resource"
                  href={lessonDocument}
                  target="_blank"
                  rel="noreferrer"
                >
                  <span aria-hidden="true">
                    📎
                  </span>

                  <span>
                    Ouvrir la ressource
                  </span>

                  <span aria-hidden="true">
                    ↗
                  </span>
                </a>
              )}

              <div className="read-page__navigation">
                <button
                  type="button"
                  className="read-page__navigation-button"
                  disabled={
                    safeLessonIndex === 0
                  }
                  onClick={
                    handlePreviousLesson
                  }
                >
                  ← Précédent
                </button>

                <div className="read-page__lesson-dots">
                  {lessons.map(
                    (
                      lesson,
                      lessonIndex
                    ) => (
                      <button
                        key={
                          lesson?.id ??
                          lessonIndex
                        }
                        type="button"
                        className={
                          lessonIndex ===
                          safeLessonIndex
                            ? 'is-active'
                            : ''
                        }
                        aria-label={`Aller à la leçon ${lessonIndex + 1}`}
                        onClick={() =>
                          handleSelectLesson(
                            lessonIndex
                          )
                        }
                      />
                    )
                  )}
                </div>

                {safeLessonIndex <
                lessons.length - 1 ? (
                  <button
                    type="button"
                    className="read-page__navigation-button read-page__navigation-button--next"
                    onClick={
                      handleNextLesson
                    }
                  >
                    Suivant →
                  </button>
                ) : (
                  <button
                    type="button"
                    className="read-page__navigation-button read-page__navigation-button--quiz"
                    disabled={
                      !quizAvailable
                    }
                    onClick={
                      handleOpenQuiz
                    }
                  >
                    Passer au quiz →
                  </button>
                )}
              </div>
            </article>
          ) : (
            <div className="read-page__empty-state">
              <span aria-hidden="true">
                📖
              </span>

              <h2>
                Aucun contenu disponible
              </h2>

              <p>
                Le contenu de ce module sera
                affiché ici lorsqu’il sera
                ajouté depuis le backend.
              </p>
            </div>
          )}
        </main>

        <aside className="read-page__journey">
          <div className="read-page__journey-card">
            <span className="read-page__journey-icon">
              💡
            </span>

            <h3>Votre parcours</h3>

            <p>
              Lisez attentivement le
              contenu, passez le quiz puis
              réalisez les challenges
              associés au module.
            </p>

            <div className="read-page__journey-steps">
              <div className="is-active">
                <span>1</span>

                <div>
                  <strong>Lecture</strong>
                  <small>En cours</small>
                </div>
              </div>

              <div
                className={
                  quizAvailable
                    ? ''
                    : 'is-disabled'
                }
              >
                <span>2</span>

                <div>
                  <strong>Quiz</strong>

                  <small>
                    {quizAvailable
                      ? 'Disponible'
                      : 'Verrouillé'}
                  </small>
                </div>
              </div>

              <div>
                <span>3</span>

                <div>
                  <strong>
                    Challenges
                  </strong>

                  <small>
                    Mise en pratique
                  </small>
                </div>
              </div>
            </div>

            <button
              type="button"
              className="read-page__quiz-action"
              disabled={!quizAvailable}
              onClick={handleOpenQuiz}
            >
              Ouvrir le quiz
            </button>

            <button
              type="button"
              className="read-page__challenge-action"
              onClick={
                handleOpenChallenge
              }
            >
              Voir les challenges
            </button>
          </div>
        </aside>
      </div>
    </section>
  )
}

export default Read