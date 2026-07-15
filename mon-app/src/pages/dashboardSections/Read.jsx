import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'

import api, { getApiErrorMessage } from '../../api/api'
import { formationApi } from '../../api/services'
import { buildDashboardUrl } from '../../utils/dashboardRoutes'

import './Read.css'

const getModuleSlug = (module) =>
  String(module?.slug || '').trim()

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

  return illustrations
    .flatMap((illustration) => {
      if (Array.isArray(illustration?.images)) {
        return illustration.images.map((image) => ({
          ...image,
          titre: illustration.titre,
          description: illustration.description,
          groupe_ordre: illustration.ordre,
        }))
      }

      return illustration
    })
    .sort(
      (firstIllustration, secondIllustration) =>
        Number(
          firstIllustration?.groupe_ordre ??
            firstIllustration?.ordre ??
            0
        ) -
        Number(
          secondIllustration?.groupe_ordre ??
            secondIllustration?.ordre ??
            0
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

const getVideoExtension = (videoUrl) => {
  const cleanUrl = String(videoUrl || '')
    .split('?')[0]
    .split('#')[0]
    .toLowerCase()

  const extensionMatch = cleanUrl.match(/\.([a-z0-9]+)$/)
  return extensionMatch?.[1] || ''
}

const getVideoMimeType = (videoUrl) => {
  const extension = getVideoExtension(videoUrl)

  const mimeTypes = {
    mp4: 'video/mp4',
    m4v: 'video/x-m4v',
    webm: 'video/webm',
    ogg: 'video/ogg',
    ogv: 'video/ogg',
    mov: 'video/quicktime',
    mkv: 'video/x-matroska',
    mk3d: 'video/x-matroska',
    mks: 'video/x-matroska',
    avi: 'video/x-msvideo',
    mpg: 'video/mpeg',
    mpeg: 'video/mpeg',
    ts: 'video/mp2t',
    m2ts: 'video/mp2t',
  }

  return mimeTypes[extension] || 'application/octet-stream'
}

const isMatroskaVideo = (videoUrl) =>
  ['mkv', 'mk3d', 'mks'].includes(
    getVideoExtension(videoUrl)
  )

const getEmbeddedVideoUrl = (videoUrl) => {
  if (!videoUrl) {
    return ''
  }

  try {
    const url = new URL(videoUrl, window.location.origin)
    const hostname = url.hostname.replace(/^www\./, '').toLowerCase()

    if (hostname === 'youtu.be') {
      const videoId = url.pathname.replace(/^\//, '').split('/')[0]
      return videoId ? `https://www.youtube.com/embed/${videoId}` : ''
    }

    if (hostname === 'youtube.com' || hostname === 'm.youtube.com') {
      const videoId =
        url.searchParams.get('v') ||
        url.pathname.match(/^\/(?:embed|shorts)\/([^/]+)/)?.[1]

      return videoId ? `https://www.youtube.com/embed/${videoId}` : ''
    }

    if (hostname === 'vimeo.com' || hostname === 'player.vimeo.com') {
      const videoId = url.pathname.match(/(?:video\/)?(\d+)/)?.[1]
      return videoId ? `https://player.vimeo.com/video/${videoId}` : ''
    }
  } catch {
    return ''
  }

  return ''
}

function Read({
  module,
  getMediaUrl,
  onBack,
  onOpenQuiz,
  onOpenChallenge,
  onMarkedRead,
}) {
  const [activeLessonIndex, setActiveLessonIndex] =
    useState(0)

  const [isMarkedRead, setIsMarkedRead] = useState(
    Boolean(module?.est_lu)
  )
  const [isMarkingRead, setIsMarkingRead] = useState(false)
  const [readMessage, setReadMessage] = useState('')
  const [readError, setReadError] = useState('')
  const [videoSource, setVideoSource] = useState('')
  const [videoError, setVideoError] = useState('')
  const [isLoadingVideoFallback, setIsLoadingVideoFallback] = useState(false)
  const videoBlobUrlRef = useRef('')
  const videoFallbackAttemptedRef = useRef(false)

  const lessons = useMemo(
    () => getModuleLessons(module),
    [module]
  )

  useEffect(() => {
    setActiveLessonIndex(0)
    setIsMarkedRead(Boolean(module?.est_lu))
    setReadMessage('')
    setReadError('')
  }, [module?.slug, module?.est_lu])

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

  const embeddedVideoUrl = getEmbeddedVideoUrl(lessonVideo)

  useEffect(() => {
    if (videoBlobUrlRef.current) {
      URL.revokeObjectURL(videoBlobUrlRef.current)
      videoBlobUrlRef.current = ''
    }

    videoFallbackAttemptedRef.current = false
    setVideoSource(embeddedVideoUrl ? '' : lessonVideo)
    setVideoError('')
    setIsLoadingVideoFallback(false)

    return () => {
      if (videoBlobUrlRef.current) {
        URL.revokeObjectURL(videoBlobUrlRef.current)
        videoBlobUrlRef.current = ''
      }
    }
  }, [embeddedVideoUrl, lessonVideo])

  const handleVideoPlaybackError = async () => {
    if (
      !lessonVideo ||
      embeddedVideoUrl ||
      videoFallbackAttemptedRef.current
    ) {
      setVideoError(
        isMatroskaVideo(lessonVideo)
          ? 'Le fichier MKV est accessible, mais son conteneur ou ses codecs ne sont pas pris en charge par ce navigateur. Une version MP4 H.264/AAC est nécessaire pour garantir la lecture en ligne.'
          : 'Cette vidéo ne peut pas être lue directement. Utilisez le lien pour l’ouvrir.'
      )
      return
    }

    videoFallbackAttemptedRef.current = true
    setIsLoadingVideoFallback(true)
    setVideoError('')

    try {
      const response = await api.get(lessonVideo, {
        responseType: 'blob',
        timeout: 120000,
      })

      const receivedBlob = response.data
      const receivedType = String(receivedBlob?.type || '')
      const expectedType = getVideoMimeType(lessonVideo)
      const playableType =
        expectedType !== 'application/octet-stream'
          ? expectedType
          : receivedType || 'application/octet-stream'

      const playableBlob =
        receivedType === playableType
          ? receivedBlob
          : new Blob([receivedBlob], {
              type: playableType,
            })

      const blobUrl = URL.createObjectURL(playableBlob)

      if (videoBlobUrlRef.current) {
        URL.revokeObjectURL(videoBlobUrlRef.current)
      }

      videoBlobUrlRef.current = blobUrl
      setVideoSource(blobUrl)
    } catch (videoRequestError) {
      console.error(
        'Impossible de charger la vidéo avec authentification :',
        videoRequestError
      )
      setVideoError(
        getApiErrorMessage(
          videoRequestError,
          'Impossible de charger cette vidéo.'
        )
      )
    } finally {
      setIsLoadingVideoFallback(false)
    }
  }

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

  const resources = Array.isArray(module?.ressources)
    ? module.ressources
    : []

  const quizAvailable =
    module?.quiz_disponible !== false

  const updateUrl = (
    section,
    view = ''
  ) => {
    if (typeof window === 'undefined' || !moduleSlug) {
      return
    }

    const nextUrl = buildDashboardUrl({
      section,
      moduleSlug,
      view: view || 'read',
    })

    window.history.pushState(
      {
        section,
        moduleSlug,
        view,
      },
      '',
      nextUrl
    )
  }

  const handleBack = () => {
    if (typeof window !== 'undefined') {
      window.history.pushState(
        { section: 'learning' },
        '',
        buildDashboardUrl({ section: 'learning' })
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
    sessionStorage.removeItem(
      'waterChallengeChallengeModuleId'
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

  const handleMarkRead = async () => {
    if (!moduleSlug || isMarkedRead || isMarkingRead) {
      return
    }

    setIsMarkingRead(true)
    setReadMessage('')
    setReadError('')

    try {
      const progression = await formationApi.markRead(moduleSlug)

      setIsMarkedRead(true)
      setReadMessage('Lecture enregistrée avec succès.')

      window.dispatchEvent(
        new CustomEvent('waterchallenge:data-updated', {
          detail: { source: 'module-read', moduleSlug },
        })
      )

      if (typeof onMarkedRead === 'function') {
        onMarkedRead(progression)
      }
    } catch (error) {
      setReadError(
        getApiErrorMessage(
          error,
          "Impossible d'enregistrer la lecture du module."
        )
      )
    } finally {
      setIsMarkingRead(false)
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

            {isMarkedRead && (
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
                  {embeddedVideoUrl ? (
                    <iframe
                      src={embeddedVideoUrl}
                      title={lessonTitle || 'Vidéo du module'}
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                      allowFullScreen
                    />
                  ) : (
                    <video
                      key={videoSource || lessonVideo}
                      src={videoSource || lessonVideo}
                      controls
                      playsInline
                      preload="metadata"
                      onCanPlay={() => setVideoError('')}
                      onError={handleVideoPlaybackError}
                    >
                      Votre navigateur ne prend pas en charge la lecture de vidéos.
                    </video>
                  )}

                  {isLoadingVideoFallback && (
                    <p className="read-page__video-status" role="status">
                      Chargement sécurisé de la vidéo…
                    </p>
                  )}

                  {videoError && (
                    <p className="read-page__video-status is-error" role="alert">
                      {videoError}{' '}
                      <a href={lessonVideo} target="_blank" rel="noreferrer">
                        Ouvrir la vidéo
                      </a>
                    </p>
                  )}
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
                                illustration?.titre ||
                                illustration?.description ||
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

                            {(illustration?.titre ||
                              illustration?.description ||
                              illustration?.legende) && (
                              <figcaption>
                                <strong>
                                  {illustration?.titre ||
                                    illustration?.legende}
                                </strong>
                                {illustration?.description && (
                                  <span>
                                    {illustration.description}
                                  </span>
                                )}
                              </figcaption>
                            )}
                          </figure>
                        )
                      }
                    )}
                  </div>
                </div>
              )}

              {(lessonDocument || resources.length > 0) && (
                <div className="read-page__resources">
                  {lessonDocument && (
                    <a
                      className="read-page__resource"
                      href={lessonDocument}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <span aria-hidden="true">📎</span>
                      <span>Ouvrir la ressource de la leçon</span>
                      <span aria-hidden="true">↗</span>
                    </a>
                  )}

                  {resources.map((resource, resourceIndex) => {
                    const resourceUrl = resolveMediaUrl(
                      resource?.fichier || resource?.url || resource
                    )

                    if (!resourceUrl) {
                      return null
                    }

                    const resourceName = String(
                      resource?.fichier || resource?.nom || ''
                    )
                      .split('/')
                      .pop()

                    return (
                      <a
                        className="read-page__resource"
                        href={resourceUrl}
                        target="_blank"
                        rel="noreferrer"
                        key={resource?.id ?? resourceIndex}
                      >
                        <span aria-hidden="true">📄</span>
                        <span>{resourceName || `Ressource ${resourceIndex + 1}`}</span>
                        <span aria-hidden="true">↗</span>
                      </a>
                    )
                  })}
                </div>
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

            {readError && (
              <p className="read-page__action-message is-error" role="alert">
                {readError}
              </p>
            )}

            {readMessage && (
              <p className="read-page__action-message is-success" role="status">
                {readMessage}
              </p>
            )}

            <button
              type="button"
              className="read-page__quiz-action"
              disabled={isMarkedRead || isMarkingRead}
              onClick={handleMarkRead}
            >
              {isMarkedRead
                ? '✓ Module marqué comme lu'
                : isMarkingRead
                  ? 'Enregistrement…'
                  : 'Marquer le module comme lu'}
            </button>

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
