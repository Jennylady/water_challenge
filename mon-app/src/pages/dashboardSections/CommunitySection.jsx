import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'

import './CommunitySection.css'

const STORAGE_KEY =
  'waterChallengeCommunityPosts'

const POSTS_PER_PAGE = 5

const MAX_ATTACHMENT_SIZE =
  1.5 * 1024 * 1024

const createDefaultPosts = () => {
  const today = new Date()

  const previousDate = new Date()
  previousDate.setDate(
    previousDate.getDate() - 4
  )

  return [
    {
      id: 1,
      authorId: 'water-ambassador',
      author: 'Water Ambassador',
      initials: 'W',
      createdAt: today.toISOString(),
      text:
        'J’ai sensibilisé ma famille sur trois gestes simples pour économiser l’eau : fermer le robinet, réutiliser l’eau de lavage et signaler les fuites.',
      mood: 'proud',
      attachment: null,
      encouragements: 12,
      encouraged: false,
      comments: [],
      isMine: false,
    },
    {
      id: 2,
      authorId: 'community-team',
      author: 'Community Team',
      initials: 'C',
      createdAt: previousDate.toISOString(),
      text:
        'Nouveau défi : créer une affiche avec un message clair sur la protection des sources d’eau.',
      mood: 'challenge',
      attachment: null,
      encouragements: 8,
      encouraged: false,
      comments: [],
      isMine: false,
    },
  ]
}

function CommunitySection({
  t,
  user,
}) {
  const photoInputRef = useRef(null)
  const videoInputRef = useRef(null)

  const [posts, setPosts] = useState(() => {
    try {
      const savedPosts =
        localStorage.getItem(STORAGE_KEY)

      if (!savedPosts) {
        return createDefaultPosts()
      }

      const parsedPosts =
        JSON.parse(savedPosts)

      return Array.isArray(parsedPosts)
        ? parsedPosts
        : createDefaultPosts()
    } catch (error) {
      console.error(
        'Impossible de récupérer les publications :',
        error
      )

      return createDefaultPosts()
    }
  })

  const [text, setText] = useState('')
  const [mood, setMood] = useState('')
  const [attachment, setAttachment] =
    useState(null)

  const [isReadingFile, setIsReadingFile] =
    useState(false)

  const [message, setMessage] = useState({
    type: '',
    text: '',
  })

  const [openMenuId, setOpenMenuId] =
    useState(null)

  const [openCommentsId, setOpenCommentsId] =
    useState(null)

  const [commentDrafts, setCommentDrafts] =
    useState({})

  const [currentPage, setCurrentPage] =
    useState(1)

  const labels = useMemo(
    () => ({
      kicker:
        t?.community?.kicker ||
        'Partage',

      title:
        t?.community?.title ||
        'Community',

      subtitle:
        t?.community?.subtitle ||
        'Partage tes expériences, pose des questions et découvre les réalisations des autres ambassadeurs.',

      publish:
        t?.community?.publish ||
        'Publier',

      placeholder:
        t?.community?.placeholder ||
        'Partage ton expérience, une question ou une réalisation...',

      photo: 'Photo',
      video: 'Vidéo',
      mood: 'Humeur',

      comment: 'Commenter',
      encourage: 'Encourager',
      encouraged: 'Encouragé',

      delete: 'Supprimer',
      hide: 'Masquer',

      send: 'Envoyer',
      cancel: 'Annuler',

      commentPlaceholder:
        'Écrire un commentaire...',

      empty:
        'Aucune publication pour le moment.',

      characters:
        'caractères restants',

      attachmentTooLarge:
        'Le fichier ne doit pas dépasser 1,5 Mo.',

      invalidFile:
        'Le fichier sélectionné est invalide.',

      publicationSaved:
        'Publication ajoutée avec succès.',

      publicationError:
        'Impossible d’enregistrer la publication.',

      required:
        'Ajoute un message, une photo ou une vidéo avant de publier.',
    }),
    [t]
  )

  const currentAuthor = useMemo(() => {
    const firstName =
      user?.first_name ||
      user?.prenom ||
      ''

    const lastName =
      user?.last_name ||
      user?.nom ||
      ''

    const fullName =
      user?.full_name ||
      `${firstName} ${lastName}`.trim() ||
      'Moi'

    const firstInitial =
      firstName?.charAt(0) ||
      fullName?.charAt(0) ||
      'M'

    const lastInitial =
      lastName?.charAt(0) ||
      fullName
        ?.split(' ')
        ?.slice(-1)[0]
        ?.charAt(0) ||
      ''

    return {
      id:
        user?.id ||
        user?.email ||
        'current-user',

      name: fullName,

      initials:
        `${firstInitial}${lastInitial}`
          .toUpperCase()
          .slice(0, 2),
    }
  }, [user])

  const savePosts = (nextPosts) => {
    setPosts(nextPosts)

    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(nextPosts)
      )
    } catch (error) {
      console.error(
        'Impossible d’enregistrer les publications :',
        error
      )

      setMessage({
        type: 'error',
        text: labels.publicationError,
      })
    }
  }

  const createId = () => {
    if (
      typeof crypto !== 'undefined' &&
      crypto.randomUUID
    ) {
      return crypto.randomUUID()
    }

    return `${Date.now()}-${Math.random()
      .toString(16)
      .slice(2)}`
  }

  const formatPostDate = (dateValue) => {
    if (!dateValue) {
      return ''
    }

    const date = new Date(dateValue)

    if (Number.isNaN(date.getTime())) {
      return String(dateValue)
    }

    const today = new Date()

    const startOfToday = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate()
    )

    const startOfDate = new Date(
      date.getFullYear(),
      date.getMonth(),
      date.getDate()
    )

    const difference =
      Math.round(
        (
          startOfDate.getTime() -
          startOfToday.getTime()
        ) /
          86400000
      )

    if (difference === 0) {
      return 'Aujourd’hui'
    }

    if (difference === -1) {
      return 'Hier'
    }

    if (
      difference < -1 &&
      difference >= -7
    ) {
      return 'Cette semaine'
    }

    return new Intl.DateTimeFormat(
      'fr-FR',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      }
    ).format(date)
  }

  const handleFileSelection = (
    event,
    type
  ) => {
    const file =
      event.target.files?.[0]

    if (!file) {
      return
    }

    const expectedPrefix =
      type === 'image'
        ? 'image/'
        : 'video/'

    if (
      !file.type.startsWith(
        expectedPrefix
      )
    ) {
      setMessage({
        type: 'error',
        text: labels.invalidFile,
      })

      event.target.value = ''
      return
    }

    if (
      file.size > MAX_ATTACHMENT_SIZE
    ) {
      setMessage({
        type: 'error',
        text: labels.attachmentTooLarge,
      })

      event.target.value = ''
      return
    }

    setIsReadingFile(true)
    setMessage({
      type: '',
      text: '',
    })

    const reader = new FileReader()

    reader.onload = () => {
      setAttachment({
        id: createId(),
        type,
        name: file.name,
        mimeType: file.type,
        size: file.size,
        url: reader.result,
      })

      setIsReadingFile(false)
    }

    reader.onerror = () => {
      setMessage({
        type: 'error',
        text: labels.invalidFile,
      })

      setIsReadingFile(false)
    }

    reader.readAsDataURL(file)
  }

  const handleRemoveAttachment = () => {
    setAttachment(null)

    if (photoInputRef.current) {
      photoInputRef.current.value = ''
    }

    if (videoInputRef.current) {
      videoInputRef.current.value = ''
    }
  }

  const handleSubmit = (event) => {
    event.preventDefault()

    const normalizedText =
      text.trim()

    if (
      !normalizedText &&
      !attachment
    ) {
      setMessage({
        type: 'error',
        text: labels.required,
      })

      return
    }

    const nextPost = {
      id: createId(),
      authorId: currentAuthor.id,
      author: currentAuthor.name,
      initials: currentAuthor.initials,
      createdAt:
        new Date().toISOString(),
      text: normalizedText,
      mood,
      attachment,
      encouragements: 0,
      encouraged: false,
      comments: [],
      isMine: true,
    }

    savePosts([
      nextPost,
      ...posts,
    ])

    setText('')
    setMood('')
    setAttachment(null)
    setCurrentPage(1)

    if (photoInputRef.current) {
      photoInputRef.current.value = ''
    }

    if (videoInputRef.current) {
      videoInputRef.current.value = ''
    }

    setMessage({
      type: 'success',
      text: labels.publicationSaved,
    })
  }

  const handleToggleEncouragement = (
    postId
  ) => {
    const nextPosts = posts.map(
      (post) => {
        if (post.id !== postId) {
          return post
        }

        const encouraged =
          !post.encouraged

        const currentCount =
          Number(
            post.encouragements || 0
          )

        return {
          ...post,
          encouraged,
          encouragements: encouraged
            ? currentCount + 1
            : Math.max(
                currentCount - 1,
                0
              ),
        }
      }
    )

    savePosts(nextPosts)
  }

  const handleDeletePost = (
    postId
  ) => {
    const nextPosts =
      posts.filter(
        (post) => post.id !== postId
      )

    savePosts(nextPosts)
    setOpenMenuId(null)
  }

  const handleCommentChange = (
    postId,
    value
  ) => {
    setCommentDrafts(
      (currentDrafts) => ({
        ...currentDrafts,
        [postId]: value,
      })
    )
  }

  const handleAddComment = (
    event,
    postId
  ) => {
    event.preventDefault()

    const commentText =
      commentDrafts[postId]?.trim()

    if (!commentText) {
      return
    }

    const nextPosts = posts.map(
      (post) => {
        if (post.id !== postId) {
          return post
        }

        const currentComments =
          Array.isArray(post.comments)
            ? post.comments
            : []

        return {
          ...post,
          comments: [
            ...currentComments,
            {
              id: createId(),
              author:
                currentAuthor.name,
              initials:
                currentAuthor.initials,
              text: commentText,
              createdAt:
                new Date().toISOString(),
            },
          ],
        }
      }
    )

    savePosts(nextPosts)

    setCommentDrafts(
      (currentDrafts) => ({
        ...currentDrafts,
        [postId]: '',
      })
    )
  }

  const moodDetails = {
    happy: {
      icon: '😊',
      label: 'Heureux',
    },
    proud: {
      icon: '💙',
      label: 'Fier',
    },
    inspired: {
      icon: '✨',
      label: 'Inspiré',
    },
    challenge: {
      icon: '🏆',
      label: 'Motivé',
    },
  }

  const totalPages = Math.max(
    1,
    Math.ceil(
      posts.length / POSTS_PER_PAGE
    )
  )

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages)
    }
  }, [
    currentPage,
    totalPages,
  ])

  const paginatedPosts = useMemo(() => {
    const startIndex =
      (currentPage - 1) *
      POSTS_PER_PAGE

    return posts.slice(
      startIndex,
      startIndex + POSTS_PER_PAGE
    )
  }, [
    posts,
    currentPage,
  ])

  const firstVisiblePost =
    posts.length === 0
      ? 0
      : (currentPage - 1) *
          POSTS_PER_PAGE +
        1

  const lastVisiblePost = Math.min(
    currentPage * POSTS_PER_PAGE,
    posts.length
  )

  const remainingCharacters =
    500 - text.length

  return (
    <section className="dash-section community-page">
      <div className="community-page__header">
        <div>
          <p className="community-page__kicker">
            {labels.kicker}
          </p>

          <h1 className="community-page__title">
            {labels.title}
          </h1>

          <p className="community-page__subtitle">
            {labels.subtitle}
          </p>
        </div>

        <span className="community-page__count">
          {posts.length}{' '}
          {posts.length > 1
            ? 'publications'
            : 'publication'}
        </span>
      </div>

      <article className="community-page__composer">
        <form onSubmit={handleSubmit}>
          <div className="community-page__composer-title">
            <span className="community-page__composer-avatar">
              {currentAuthor.initials}
            </span>

            <div>
              <h2>{labels.publish}</h2>
              <p>
                Partage une expérience avec
                la communauté
              </p>
            </div>
          </div>

          <div className="community-page__textarea-wrapper">
            <textarea
              value={text}
              maxLength={500}
              onChange={(event) =>
                setText(event.target.value)
              }
              placeholder={
                labels.placeholder
              }
              aria-label={
                labels.placeholder
              }
            />

            <small>
              {remainingCharacters}{' '}
              {labels.characters}
            </small>
          </div>

          {attachment && (
            <div className="community-page__attachment-preview">
              {attachment.type ===
              'image' ? (
                <img
                  src={attachment.url}
                  alt={attachment.name}
                />
              ) : (
                <video
                  src={attachment.url}
                  controls
                />
              )}

              <div>
                <strong>
                  {attachment.name}
                </strong>

                <small>
                  {attachment.type ===
                  'image'
                    ? 'Image'
                    : 'Vidéo'}
                </small>
              </div>

              <button
                type="button"
                onClick={
                  handleRemoveAttachment
                }
                aria-label="Retirer le fichier"
              >
                ×
              </button>
            </div>
          )}

          {message.text && (
            <div
              className={`community-page__message community-page__message--${message.type}`}
              role="alert"
            >
              <span>
                {message.type ===
                'success'
                  ? '✓'
                  : '⚠️'}
              </span>

              <p>{message.text}</p>

              <button
                type="button"
                onClick={() =>
                  setMessage({
                    type: '',
                    text: '',
                  })
                }
              >
                ×
              </button>
            </div>
          )}

          <div className="community-page__composer-footer">
            <div className="community-page__composer-tools">
              <input
                ref={photoInputRef}
                type="file"
                accept="image/*"
                hidden
                onChange={(event) =>
                  handleFileSelection(
                    event,
                    'image'
                  )
                }
              />

              <input
                ref={videoInputRef}
                type="file"
                accept="video/*"
                hidden
                onChange={(event) =>
                  handleFileSelection(
                    event,
                    'video'
                  )
                }
              />

              <button
                type="button"
                onClick={() =>
                  photoInputRef.current?.click()
                }
              >
                <span>📷</span>
                {labels.photo}
              </button>

              <button
                type="button"
                onClick={() =>
                  videoInputRef.current?.click()
                }
              >
                <span>🎥</span>
                {labels.video}
              </button>

              <label className="community-page__mood">
                <span>😊</span>

                <select
                  value={mood}
                  onChange={(event) =>
                    setMood(
                      event.target.value
                    )
                  }
                >
                  <option value="">
                    {labels.mood}
                  </option>

                  <option value="happy">
                    Heureux
                  </option>

                  <option value="proud">
                    Fier
                  </option>

                  <option value="inspired">
                    Inspiré
                  </option>

                  <option value="challenge">
                    Motivé
                  </option>
                </select>
              </label>
            </div>

            <button
              type="submit"
              className="community-page__publish"
              disabled={isReadingFile}
            >
              {isReadingFile
                ? 'Préparation...'
                : labels.publish}
            </button>
          </div>
        </form>
      </article>

      {paginatedPosts.length === 0 ? (
        <div className="community-page__empty">
          <span>💬</span>
          <p>{labels.empty}</p>
        </div>
      ) : (
        <div className="community-page__feed">
          {paginatedPosts.map(
            (post) => {
              const comments =
                Array.isArray(
                  post.comments
                )
                  ? post.comments
                  : []

              const isCommentOpen =
                openCommentsId ===
                post.id

              const isMenuOpen =
                openMenuId === post.id

              const postMood =
                moodDetails[post.mood]

              return (
                <article
                  className="community-page__post"
                  key={post.id}
                >
                  <header className="community-page__post-header">
                    <div className="community-page__post-author">
                      <span className="community-page__post-avatar">
                        {post.initials ||
                          post.author
                            ?.charAt(0)
                            ?.toUpperCase() ||
                          'W'}
                      </span>

                      <div>
                        <strong>
                          {post.author}
                        </strong>

                        <small>
                          {formatPostDate(
                            post.createdAt ||
                              post.date
                          )}
                        </small>
                      </div>
                    </div>

                    <div className="community-page__post-menu">
                      <button
                        type="button"
                        onClick={() =>
                          setOpenMenuId(
                            isMenuOpen
                              ? null
                              : post.id
                          )
                        }
                        aria-label="Options de la publication"
                      >
                        •••
                      </button>

                      {isMenuOpen && (
                        <div className="community-page__post-menu-panel">
                          <button
                            type="button"
                            onClick={() =>
                              handleDeletePost(
                                post.id
                              )
                            }
                          >
                            {post.isMine
                              ? labels.delete
                              : labels.hide}
                          </button>
                        </div>
                      )}
                    </div>
                  </header>

                  {postMood && (
                    <span className="community-page__post-mood">
                      {postMood.icon}{' '}
                      {postMood.label}
                    </span>
                  )}

                  {post.text && (
                    <p className="community-page__post-text">
                      {post.text}
                    </p>
                  )}

                  {post.attachment && (
                    <div className="community-page__post-media">
                      {post.attachment
                        .type ===
                      'image' ? (
                        <img
                          src={
                            post
                              .attachment
                              .url
                          }
                          alt={
                            post
                              .attachment
                              .name ||
                            'Publication'
                          }
                        />
                      ) : (
                        <video
                          src={
                            post
                              .attachment
                              .url
                          }
                          controls
                        />
                      )}
                    </div>
                  )}

                  <footer className="community-page__post-footer">
                    <div className="community-page__post-actions">
                      <button
                        type="button"
                        className={
                          isCommentOpen
                            ? 'is-active'
                            : ''
                        }
                        onClick={() =>
                          setOpenCommentsId(
                            isCommentOpen
                              ? null
                              : post.id
                          )
                        }
                      >
                        <span>💬</span>

                        {labels.comment}

                        {comments.length >
                          0 && (
                          <strong>
                            {
                              comments.length
                            }
                          </strong>
                        )}
                      </button>

                      <button
                        type="button"
                        className={
                          post.encouraged
                            ? 'is-encouraged'
                            : ''
                        }
                        onClick={() =>
                          handleToggleEncouragement(
                            post.id
                          )
                        }
                      >
                        <span>👏</span>

                        {post.encouraged
                          ? labels.encouraged
                          : labels.encourage}
                      </button>
                    </div>

                    <span className="community-page__likes">
                      ❤️{' '}
                      {Number(
                        post.encouragements ||
                          0
                      )}
                    </span>
                  </footer>

                  {isCommentOpen && (
                    <div className="community-page__comments">
                      {comments.length >
                        0 && (
                        <div className="community-page__comments-list">
                          {comments.map(
                            (comment) => (
                              <div
                                className="community-page__comment"
                                key={
                                  comment.id
                                }
                              >
                                <span>
                                  {comment.initials ||
                                    comment.author
                                      ?.charAt(
                                        0
                                      )}
                                </span>

                                <div>
                                  <strong>
                                    {
                                      comment.author
                                    }
                                  </strong>

                                  <p>
                                    {
                                      comment.text
                                    }
                                  </p>

                                  <small>
                                    {formatPostDate(
                                      comment.createdAt
                                    )}
                                  </small>
                                </div>
                              </div>
                            )
                          )}
                        </div>
                      )}

                      <form
                        className="community-page__comment-form"
                        onSubmit={(event) =>
                          handleAddComment(
                            event,
                            post.id
                          )
                        }
                      >
                        <span>
                          {
                            currentAuthor.initials
                          }
                        </span>

                        <input
                          type="text"
                          value={
                            commentDrafts[
                              post.id
                            ] || ''
                          }
                          onChange={(
                            event
                          ) =>
                            handleCommentChange(
                              post.id,
                              event.target
                                .value
                            )
                          }
                          placeholder={
                            labels.commentPlaceholder
                          }
                        />

                        <button type="submit">
                          {labels.send}
                        </button>
                      </form>
                    </div>
                  )}
                </article>
              )
            }
          )}
        </div>
      )}

      <div className="community-page__pagination">
        <div>
          <button
            type="button"
            disabled={currentPage === 1}
            onClick={() =>
              setCurrentPage(
                (page) =>
                  Math.max(page - 1, 1)
              )
            }
            aria-label="Page précédente"
          >
            ‹
          </button>

          {Array.from(
            {
              length: totalPages,
            },
            (_, index) => index + 1
          )
            .slice(0, 5)
            .map((page) => (
              <button
                type="button"
                key={page}
                className={
                  currentPage === page
                    ? 'is-active'
                    : ''
                }
                onClick={() =>
                  setCurrentPage(page)
                }
              >
                {page}
              </button>
            ))}

          <button
            type="button"
            disabled={
              currentPage ===
              totalPages
            }
            onClick={() =>
              setCurrentPage(
                (page) =>
                  Math.min(
                    page + 1,
                    totalPages
                  )
              )
            }
            aria-label="Page suivante"
          >
            ›
          </button>
        </div>

        <p>
          Affichage de {firstVisiblePost} à{' '}
          {lastVisiblePost} sur{' '}
          {posts.length} publication
          {posts.length > 1 ? 's' : ''}
        </p>
      </div>
    </section>
  )
}

export default CommunitySection