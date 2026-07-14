import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'

import api from '../../api/api'
import { getCookie } from '../../utils/cookies'

const ENDPOINT = '/challenges/defis/'
const CHALLENGES_PER_PAGE = 4

const SELECTED_CHALLENGE_KEY =
  'waterChallengeSelectedChallenge'

const CURRENT_CHALLENGE_KEY =
  'waterChallengeCurrentChallenge'

const CHALLENGE_MODULE_KEY =
  'waterChallengeChallengeModule'

const CHALLENGE_MODULE_ID_KEY =
  'waterChallengeChallengeModuleId'

const CHALLENGE_MODULE_SLUG_KEY =
  'waterChallengeChallengeModuleSlug'

/* =========================================================
   UTILITAIRES
   ========================================================= */

const normalizeText = (value) => {
  return String(value || '')
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

const normalizeIdentifier = (value) => {
  return String(value || '').trim()
}

const getChallengeModuleId = (challenge) => {
  const moduleValue = challenge?.module

  const value =
    challenge?.module_id ??
    challenge?.module_uuid ??
    challenge?.formation_module_id ??
    challenge?.module_detail?.id ??
    (
      moduleValue &&
      typeof moduleValue === 'object'
        ? moduleValue.id
        : moduleValue
    ) ??
    ''

  return normalizeIdentifier(value)
}

const getChallengeModuleSlug = (challenge) => {
  const moduleValue = challenge?.module

  const value =
    challenge?.module_slug ??
    challenge?.formation_module_slug ??
    challenge?.module_detail?.slug ??
    (
      moduleValue &&
      typeof moduleValue === 'object'
        ? moduleValue.slug
        : ''
    ) ??
    ''

  return normalizeIdentifier(value)
}

const getChallengeModuleTitle = (challenge) => {
  const moduleValue = challenge?.module

  const value =
    challenge?.module_titre ??
    challenge?.formation_module_titre ??
    challenge?.module_detail?.titre ??
    (
      moduleValue &&
      typeof moduleValue === 'object'
        ? (
            moduleValue.titre ??
            moduleValue.title
          )
        : ''
    ) ??
    ''

  return String(value || '').trim()
}

const readStoredModule = () => {
  if (typeof window === 'undefined') {
    return null
  }

  try {
    const storedValue =
      sessionStorage.getItem(
        CHALLENGE_MODULE_KEY
      )

    if (!storedValue) {
      return null
    }

    const parsedModule =
      JSON.parse(storedValue)

    return (
      parsedModule &&
      typeof parsedModule === 'object'
        ? parsedModule
        : null
    )
  } catch (storageError) {
    console.error(
      'Impossible de récupérer le module enregistré :',
      storageError
    )

    return null
  }
}

/**
 * Le filtrage n’est actif que lorsque l’URL contient :
 *
 * ?section=challenges&module=slug
 *
 * ou :
 *
 * ?section=challenges&moduleId=uuid
 *
 * Sans ces paramètres, tous les challenges sont affichés.
 */
const getModuleFilterFromLocation = () => {
  const emptyFilter = {
    isActive: false,
    moduleId: '',
    moduleSlug: '',
    moduleTitle: '',
  }

  if (typeof window === 'undefined') {
    return emptyFilter
  }

  const searchParams =
    new URLSearchParams(
      window.location.search
    )

  const urlModuleId =
    normalizeIdentifier(
      searchParams.get('moduleId')
    )

  const urlModuleSlug =
    normalizeIdentifier(
      searchParams.get('module')
    )

  const isActive = Boolean(
    urlModuleId ||
    urlModuleSlug
  )

  if (!isActive) {
    return emptyFilter
  }

  const storedModule =
    readStoredModule()

  const storedModuleId =
    normalizeIdentifier(
      storedModule?.id ||
      sessionStorage.getItem(
        CHALLENGE_MODULE_ID_KEY
      )
    )

  const storedModuleSlug =
    normalizeIdentifier(
      storedModule?.slug ||
      sessionStorage.getItem(
        CHALLENGE_MODULE_SLUG_KEY
      )
    )

  const storedModuleTitle =
    String(
      storedModule?.titre ||
      storedModule?.title ||
      ''
    ).trim()

  const idMatches = Boolean(
    urlModuleId &&
    storedModuleId &&
    urlModuleId === storedModuleId
  )

  const slugMatches = Boolean(
    urlModuleSlug &&
    storedModuleSlug &&
    normalizeText(urlModuleSlug) ===
      normalizeText(storedModuleSlug)
  )

  const storageMatchesUrl =
    idMatches || slugMatches

  return {
    isActive: true,

    moduleId:
      urlModuleId ||
      (
        storageMatchesUrl
          ? storedModuleId
          : ''
      ),

    moduleSlug:
      urlModuleSlug ||
      (
        storageMatchesUrl
          ? storedModuleSlug
          : ''
      ),

    moduleTitle:
      storageMatchesUrl
        ? storedModuleTitle
        : '',
  }
}

const parseCriteria = (value) => {
  if (!value) {
    return []
  }

  if (Array.isArray(value)) {
    return value
      .map((item) =>
        String(item).trim()
      )
      .filter(Boolean)
  }

  if (typeof value === 'object') {
    return Object.values(value)
      .map((item) =>
        String(item).trim()
      )
      .filter(Boolean)
  }

  const text = String(value).trim()

  if (!text) {
    return []
  }

  try {
    const parsedValue = JSON.parse(text)

    if (Array.isArray(parsedValue)) {
      return parsedValue
        .map((item) =>
          String(item).trim()
        )
        .filter(Boolean)
    }

    if (
      parsedValue &&
      typeof parsedValue === 'object'
    ) {
      return Object.values(parsedValue)
        .map((item) =>
          String(item).trim()
        )
        .filter(Boolean)
    }
  } catch {
    // La valeur n’est pas du JSON.
  }

  return text
    .split(/\r?\n|;|•|\|/)
    .map((item) =>
      item
        .replace(/^[-–—]\s*/, '')
        .trim()
    )
    .filter(Boolean)
}

const formatLevel = (value) => {
  const normalizedLevel =
    normalizeText(value)

  const levels = {
    debutant: 'Débutant',
    beginner: 'Débutant',

    intermediaire: 'Intermédiaire',
    intermediate: 'Intermédiaire',

    avance: 'Avancé',
    advanced: 'Avancé',

    expert: 'Expert',
  }

  return (
    levels[normalizedLevel] ||
    value ||
    'Tous niveaux'
  )
}

const getChallengeState = (challenge) => {
  const status =
    normalizeText(
      challenge?.statut
    )

  const submissionStatus =
    normalizeText(
      challenge
        ?.derniere_soumission
        ?.statut
    )

  const lockedStatuses = [
    'verrouille',
    'locked',
    'indisponible',
  ]

  const pendingStatuses = [
    'en_attente',
    'pending',
    'soumis',
    'submitted',
  ]

  const completedStatuses = [
    'termine',
    'terminee',
    'completed',
    'complete',
    'valide',
    'validee',
    'validated',
    'accepte',
    'acceptee',
    'accepted',
  ]

  const rejectedStatuses = [
    'rejete',
    'rejetee',
    'rejected',
    'refuse',
    'refusee',
  ]

  if (
    challenge?.est_accessible === false ||
    lockedStatuses.includes(status)
  ) {
    return {
      key: 'locked',
      label: 'Verrouillé',
      icon: '🔒',
      pillClass: 'dash-pill red',
    }
  }

  if (
    Boolean(challenge?.termine_le) ||
    completedStatuses.includes(status) ||
    completedStatuses.includes(
      submissionStatus
    )
  ) {
    return {
      key: 'completed',
      label: 'Terminé',
      icon: '✅',
      pillClass: 'dash-pill green',
    }
  }

  if (
    Boolean(
      challenge
        ?.a_soumission_en_attente
    ) ||
    pendingStatuses.includes(
      submissionStatus
    )
  ) {
    return {
      key: 'pending',
      label: 'En attente',
      icon: '⏳',
      pillClass: 'dash-pill gold',
    }
  }

  if (
    rejectedStatuses.includes(
      submissionStatus
    )
  ) {
    return {
      key: 'rejected',
      label: 'À corriger',
      icon: '↻',
      pillClass: 'dash-pill red',
    }
  }

  if (
    Boolean(challenge?.commence_le) ||
    [
      'en_cours',
      'started',
      'commence',
      'commencee',
    ].includes(status)
  ) {
    return {
      key: 'started',
      label: 'En cours',
      icon: '▶',
      pillClass: 'dash-pill',
    }
  }

  return {
    key: 'available',
    label: 'Disponible',
    icon: '🏆',
    pillClass: 'dash-pill green',
  }
}

const resolveImageUrl = (imageUrl) => {
  if (!imageUrl) {
    return ''
  }

  if (
    imageUrl.startsWith('http://') ||
    imageUrl.startsWith('https://') ||
    imageUrl.startsWith('data:') ||
    imageUrl.startsWith('blob:')
  ) {
    return imageUrl
  }

  try {
    const baseUrl =
      api?.defaults?.baseURL ||
      window.location.origin

    const apiOrigin =
      new URL(
        baseUrl,
        window.location.origin
      ).origin

    return imageUrl.startsWith('/')
      ? `${apiOrigin}${imageUrl}`
      : `${apiOrigin}/${imageUrl}`
  } catch {
    return imageUrl
  }
}

const getVisiblePages = (
  currentPage,
  totalPages
) => {
  if (totalPages <= 5) {
    return Array.from(
      {
        length: totalPages,
      },
      (_, index) => index + 1
    )
  }

  let startPage =
    currentPage - 2

  let endPage =
    currentPage + 2

  if (startPage < 1) {
    startPage = 1
    endPage = 5
  }

  if (endPage > totalPages) {
    endPage = totalPages
    startPage =
      totalPages - 4
  }

  return Array.from(
    {
      length:
        endPage -
        startPage +
        1,
    },
    (_, index) =>
      startPage + index
  )
}

/* =========================================================
   COMPOSANT
   ========================================================= */

function ChallengesSection({
  t,
  setActiveSection,
}) {
  const [
    challenges,
    setChallenges,
  ] = useState([])

  const [
    isLoading,
    setIsLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState('')

  const [
    currentPage,
    setCurrentPage,
  ] = useState(1)

  const [
    moduleFilter,
    setModuleFilter,
  ] = useState(() =>
    getModuleFilterFromLocation()
  )

  const labels = useMemo(
    () => ({
      kicker:
        t?.challenges?.kicker ||
        'Passe à l’action',

      title:
        t?.challenges?.title ||
        'Challenges',

      subtitle:
        t?.challenges?.subtitle ||
        'Réalise des actions concrètes et partage les preuves de ton activité.',

      objective:
        t?.challenges?.objective ||
        'Objectif',

      difficulty:
        t?.challenges?.difficulty ||
        'Niveau',

      duration:
        t?.challenges?.duration ||
        'Durée',

      instructions:
        t?.challenges?.instructions ||
        'Critères de validation',

      submit:
        t?.challenges?.submit ||
        'Soumettre mon activité',

      expectedResult:
        'Résultat attendu',

      requiredProofs:
        'Preuves demandées',

      retry:
        'Réessayer',

      empty:
        'Aucun défi disponible pour le moment.',

      previous:
        'Précédent',

      next:
        'Suivant',
    }),
    [t]
  )

  /* =======================================================
     CHARGEMENT DES CHALLENGES
     ======================================================= */

  const loadChallenges =
    useCallback(async () => {
      setIsLoading(true)
      setError('')

      try {
        const accessToken =
          getCookie('accessToken') ||
          getCookie('access') ||
          ''

        const response =
          await api.get(
            ENDPOINT,
            {
              headers: accessToken
                ? {
                    Authorization:
                      `Bearer ${accessToken}`,
                  }
                : {},
            }
          )

        const responseData =
          response?.data || {}

        if (
          responseData.success === false
        ) {
          throw new Error(
            responseData.erreur ||
            responseData.detail ||
            responseData.message ||
            'Impossible de récupérer les défis.'
          )
        }

        const receivedChallenges =
          Array.isArray(
            responseData.defis
          )
            ? responseData.defis
            : Array.isArray(
                responseData.challenges
              )
              ? responseData.challenges
              : Array.isArray(
                  responseData.results
                )
                ? responseData.results
                : []

        const sortedChallenges = [
          ...receivedChallenges,
        ].sort(
          (
            firstChallenge,
            secondChallenge
          ) => {
            return (
              Number(
                firstChallenge
                  ?.ordre ?? 0
              ) -
              Number(
                secondChallenge
                  ?.ordre ?? 0
              )
            )
          }
        )

        setChallenges(
          sortedChallenges
        )

        setCurrentPage(1)
      } catch (requestError) {
        console.error(
          'Erreur de récupération des défis :',
          requestError
        )

        const status =
          requestError
            ?.response
            ?.status

        const responseData =
          requestError
            ?.response
            ?.data

        if (status === 401) {
          setError(
            'Votre session a expiré. Veuillez vous reconnecter.'
          )
        } else if (status === 403) {
          setError(
            responseData?.erreur ||
            responseData?.detail ||
            responseData?.message ||
            'Vous n’avez pas accès aux défis.'
          )
        } else {
          setError(
            responseData?.erreur ||
            responseData?.detail ||
            responseData?.message ||
            requestError?.message ||
            'Impossible de charger les défis.'
          )
        }

        setChallenges([])
        setCurrentPage(1)
      } finally {
        setIsLoading(false)
      }
    }, [])

  useEffect(() => {
    loadChallenges()
  }, [loadChallenges])

  /**
   * Synchronise le filtre avec les boutons
   * précédent et suivant du navigateur.
   */
  useEffect(() => {
    const handlePopState = () => {
      setModuleFilter(
        getModuleFilterFromLocation()
      )

      setCurrentPage(1)
    }

    window.addEventListener(
      'popstate',
      handlePopState
    )

    return () => {
      window.removeEventListener(
        'popstate',
        handlePopState
      )
    }
  }, [])

  /* =======================================================
     FILTRAGE
     ======================================================= */

  const filteredChallenges =
    useMemo(() => {
      if (!moduleFilter.isActive) {
        return challenges
      }

      return challenges.filter(
        (challenge) => {
          const challengeModuleId =
            getChallengeModuleId(
              challenge
            )

          const challengeModuleSlug =
            getChallengeModuleSlug(
              challenge
            )

          const matchesId = Boolean(
            moduleFilter.moduleId &&
            challengeModuleId &&
            moduleFilter.moduleId ===
              challengeModuleId
          )

          const matchesSlug = Boolean(
            moduleFilter.moduleSlug &&
            challengeModuleSlug &&
            normalizeText(
              moduleFilter.moduleSlug
            ) ===
              normalizeText(
                challengeModuleSlug
              )
          )

          return (
            matchesId ||
            matchesSlug
          )
        }
      )
    }, [
      challenges,
      moduleFilter,
    ])

  /**
   * Si le titre n’était pas disponible dans
   * sessionStorage, on tente de le retrouver
   * à partir des challenges reçus.
   */
  const currentModuleLabel =
    useMemo(() => {
      if (!moduleFilter.isActive) {
        return ''
      }

      if (moduleFilter.moduleTitle) {
        return moduleFilter.moduleTitle
      }

      const matchingChallenge =
        filteredChallenges[0]

      return (
        getChallengeModuleTitle(
          matchingChallenge
        ) ||
        moduleFilter.moduleSlug ||
        moduleFilter.moduleId ||
        'Module sélectionné'
      )
    }, [
      filteredChallenges,
      moduleFilter,
    ])

  /* =======================================================
     PAGINATION
     ======================================================= */

  const totalPages =
    useMemo(() => {
      return Math.max(
        1,
        Math.ceil(
          filteredChallenges.length /
          CHALLENGES_PER_PAGE
        )
      )
    }, [
      filteredChallenges.length,
    ])

  const paginatedChallenges =
    useMemo(() => {
      const startIndex =
        (
          currentPage - 1
        ) *
        CHALLENGES_PER_PAGE

      const endIndex =
        startIndex +
        CHALLENGES_PER_PAGE

      return filteredChallenges.slice(
        startIndex,
        endIndex
      )
    }, [
      currentPage,
      filteredChallenges,
    ])

  const visiblePages =
    useMemo(() => {
      return getVisiblePages(
        currentPage,
        totalPages
      )
    }, [
      currentPage,
      totalPages,
    ])

  const firstDisplayedItem =
    filteredChallenges.length === 0
      ? 0
      : (
          (
            currentPage - 1
          ) *
          CHALLENGES_PER_PAGE
        ) + 1

  const lastDisplayedItem =
    Math.min(
      currentPage *
      CHALLENGES_PER_PAGE,
      filteredChallenges.length
    )

  useEffect(() => {
    if (
      currentPage > totalPages
    ) {
      setCurrentPage(
        totalPages
      )
    }
  }, [
    currentPage,
    totalPages,
  ])

  const handlePageChange =
    useCallback(
      (page) => {
        if (
          page < 1 ||
          page > totalPages ||
          page === currentPage
        ) {
          return
        }

        setCurrentPage(page)

        window.scrollTo({
          top: 0,
          behavior: 'smooth',
        })
      },
      [
        currentPage,
        totalPages,
      ]
    )

  /* =======================================================
     RETIRER LE FILTRE DU MODULE
     ======================================================= */

  const handleShowAllChallenges =
    useCallback(() => {
      const nextUrl = new URL(
        window.location.href
      )

      nextUrl.searchParams.set(
        'section',
        'challenges'
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
          section: 'challenges',
        },
        '',
        nextUrl
      )

      try {
        sessionStorage.removeItem(
          CHALLENGE_MODULE_ID_KEY
        )

        sessionStorage.removeItem(
          CHALLENGE_MODULE_SLUG_KEY
        )

        sessionStorage.removeItem(
          CHALLENGE_MODULE_KEY
        )
      } catch (storageError) {
        console.error(
          'Impossible de nettoyer le module enregistré :',
          storageError
        )
      }

      setModuleFilter({
        isActive: false,
        moduleId: '',
        moduleSlug: '',
        moduleTitle: '',
      })

      setCurrentPage(1)

      window.scrollTo({
        top: 0,
        behavior: 'smooth',
      })
    }, [])

  /* =======================================================
     SÉLECTION D’UN CHALLENGE
     ======================================================= */

  const saveSelectedChallenge =
    useCallback((challenge) => {
      const selectedChallenge = {
        ...challenge,

        selectedAt:
          new Date().toISOString(),
      }

      try {
        sessionStorage.setItem(
          SELECTED_CHALLENGE_KEY,
          JSON.stringify(
            selectedChallenge
          )
        )

        sessionStorage.setItem(
          CURRENT_CHALLENGE_KEY,
          JSON.stringify(
            selectedChallenge
          )
        )
      } catch (storageError) {
        console.error(
          'Impossible d’enregistrer le défi sélectionné :',
          storageError
        )
      }
    }, [])

  const handleChallengeAction =
    useCallback(
      (challenge) => {
        const state =
          getChallengeState(
            challenge
          )

        if (
          state.key === 'locked'
        ) {
          return
        }

        saveSelectedChallenge(
          challenge
        )

        if (
          typeof setActiveSection !==
          'function'
        ) {
          return
        }

        if (
          state.key === 'pending' ||
          state.key === 'completed'
        ) {
          setActiveSection(
            'activities'
          )

          return
        }

        setActiveSection('submit')
      },
      [
        saveSelectedChallenge,
        setActiveSection,
      ]
    )

  const getButtonLabel =
    useCallback(
      (challenge) => {
        const state =
          getChallengeState(
            challenge
          )

        switch (state.key) {
          case 'locked':
            return 'Défi verrouillé'

          case 'pending':
            return 'Voir ma soumission'

          case 'completed':
            return 'Voir mon activité'

          case 'started':
            return 'Continuer le défi'

          case 'rejected':
            return 'Corriger ma soumission'

          case 'available':
          default:
            return labels.submit
        }
      },
      [labels.submit]
    )

  /* =======================================================
     AFFICHAGE
     ======================================================= */

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">
            {labels.kicker}
          </p>

          <h1>{labels.title}</h1>

          <p>
            {moduleFilter.isActive
              ? `Challenges associés au module ${currentModuleLabel}.`
              : labels.subtitle}
          </p>
        </div>

        {!isLoading && !error && (
          <span className="dash-pill">
            🏆{' '}
            {filteredChallenges.length}{' '}
            {filteredChallenges.length > 1
              ? 'défis'
              : 'défi'}
          </span>
        )}
      </div>

      {moduleFilter.isActive &&
        !isLoading &&
        !error && (
          <div
            className="dash-form-note"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent:
                'space-between',
              flexWrap: 'wrap',
              gap: '12px',
            }}
          >
            <span>
              📚 Challenges du module{' '}
              <strong>
                {currentModuleLabel}
              </strong>
            </span>

            <button
              type="button"
              className="dash-light-btn"
              onClick={
                handleShowAllChallenges
              }
            >
              Voir tous les challenges
            </button>
          </div>
        )}

      {/* CHARGEMENT */}

      {isLoading && (
        <div className="dash-grid-2">
          {[1, 2, 3, 4].map(
            (item) => (
              <article
                className="dash-card"
                key={item}
              >
                <div className="dash-card-top">
                  <div>
                    <span className="dash-pill">
                      Chargement...
                    </span>

                    <h3>
                      Chargement du défi
                    </h3>
                  </div>

                  <span className="dash-pill gold">
                    ...
                  </span>
                </div>

                <p>
                  Récupération des
                  informations du défi...
                </p>
              </article>
            )
          )}
        </div>
      )}

      {/* ERREUR */}

      {!isLoading && error && (
        <div className="dash-form-card">
          <div className="dash-card-top">
            <div>
              <span className="dash-pill red">
                ⚠️ Erreur
              </span>

              <h3>
                Impossible de charger
                les défis
              </h3>
            </div>
          </div>

          <p className="dash-form-note">
            {error}
          </p>

          <div className="dash-actions-row">
            <button
              type="button"
              className="dash-primary-btn"
              onClick={loadChallenges}
            >
              {labels.retry}
            </button>
          </div>
        </div>
      )}

      {/* LISTE VIDE */}

      {!isLoading &&
        !error &&
        filteredChallenges.length ===
          0 && (
          <div className="dash-empty">
            <p>
              {moduleFilter.isActive
                ? `Aucun challenge n’est associé au module ${currentModuleLabel}.`
                : labels.empty}
            </p>

            {moduleFilter.isActive && (
              <button
                type="button"
                className="dash-light-btn"
                onClick={
                  handleShowAllChallenges
                }
              >
                Afficher tous les
                challenges
              </button>
            )}
          </div>
        )}

      {/* CHALLENGES */}

      {!isLoading &&
        !error &&
        filteredChallenges.length > 0 && (
          <>
            <div className="dash-grid-2">
              {paginatedChallenges.map(
                (challenge) => {
                  const state =
                    getChallengeState(
                      challenge
                    )

                  const criteria =
                    parseCriteria(
                      challenge
                        ?.criteres_validation
                    )

                  const minimumPhotos =
                    Number(
                      challenge
                        ?.nombre_photos_min ??
                      0
                    )

                  const maximumPhotos =
                    Number(
                      challenge
                        ?.nombre_photos_max ??
                      0
                    )

                  const coverImage =
                    resolveImageUrl(
                      challenge
                        ?.image_couverture_url ??
                      challenge
                        ?.image_couverture ??
                      challenge?.image
                    )

                  const isLocked =
                    state.key ===
                    'locked'

                  const challengeModuleTitle =
                    getChallengeModuleTitle(
                      challenge
                    ) ||
                    'Water Challenge'

                  return (
                    <article
                      className="dash-card module-card"
                      key={
                        challenge?.id ??
                        `${getChallengeModuleId(
                          challenge
                        )}-${challenge?.ordre}`
                      }
                    >
                      {coverImage && (
                        <div
                          className="module-image"
                          style={{
                            backgroundImage:
                              `url("${coverImage}")`,
                          }}
                          role="img"
                          aria-label={
                            challenge?.titre ||
                            'Image du défi'
                          }
                        />
                      )}

                      <div className="module-body">
                        <div className="dash-card-top">
                          <div>
                            <span className="dash-pill">
                              {
                                challengeModuleTitle
                              }
                            </span>

                            <h3>
                              {challenge?.titre ||
                                'Défi'}
                            </h3>
                          </div>

                          <span className="dash-pill gold">
                            {Number(
                              challenge
                                ?.points_recompense ??
                              challenge?.points ??
                              0
                            )}{' '}
                            pts
                          </span>
                        </div>

                        <div className="challenge-meta">
                          <span
                            className={
                              state.pillClass
                            }
                          >
                            {state.icon}{' '}
                            {state.label}
                          </span>

                          <span className="dash-pill">
                            🎯{' '}
                            {labels.difficulty}
                            {' : '}
                            {formatLevel(
                              challenge?.niveau
                            )}
                          </span>

                          {challenge
                            ?.duree_estimee && (
                            <span className="dash-pill green">
                              ⏱️{' '}
                              {labels.duration}
                              {' : '}
                              {
                                challenge
                                  .duree_estimee
                              }
                            </span>
                          )}

                          {challenge
                            ?.est_obligatoire && (
                            <span className="dash-pill red">
                              📌 Obligatoire
                            </span>
                          )}
                        </div>

                        {challenge
                          ?.description && (
                          <p>
                            <strong>
                              {labels.objective}
                              {' : '}
                            </strong>

                            {
                              challenge
                                .description
                            }
                          </p>
                        )}

                        {challenge
                          ?.resultat_attendu && (
                          <>
                            <h3
                              style={{
                                marginTop:
                                  '18px',
                              }}
                            >
                              {
                                labels
                                  .expectedResult
                              }
                            </h3>

                            <p>
                              {
                                challenge
                                  .resultat_attendu
                              }
                            </p>
                          </>
                        )}

                        {criteria.length > 0 && (
                          <>
                            <h3
                              style={{
                                marginTop:
                                  '18px',
                              }}
                            >
                              {
                                labels
                                  .instructions
                              }
                            </h3>

                            <ul className="challenge-instructions">
                              {criteria.map(
                                (
                                  criterion,
                                  criterionIndex
                                ) => (
                                  <li
                                    key={`${challenge.id}-criterion-${criterionIndex}`}
                                  >
                                    {criterion}
                                  </li>
                                )
                              )}
                            </ul>
                          </>
                        )}

                        <h3
                          style={{
                            marginTop:
                              '18px',
                          }}
                        >
                          {
                            labels
                              .requiredProofs
                          }
                        </h3>

                        <div className="challenge-meta">
                          {minimumPhotos > 0 && (
                            <span className="dash-pill">
                              📷 Minimum{' '}
                              {minimumPhotos}{' '}
                              photo
                              {minimumPhotos > 1
                                ? 's'
                                : ''}
                            </span>
                          )}

                          {maximumPhotos > 0 && (
                            <span className="dash-pill">
                              🖼️ Maximum{' '}
                              {maximumPhotos}{' '}
                              photo
                              {maximumPhotos > 1
                                ? 's'
                                : ''}
                            </span>
                          )}

                          {challenge
                            ?.video_obligatoire && (
                            <span className="dash-pill red">
                              🎥 Vidéo
                              obligatoire
                            </span>
                          )}

                          {minimumPhotos === 0 &&
                            maximumPhotos === 0 &&
                            !challenge
                              ?.video_obligatoire && (
                              <span className="dash-pill">
                                📄 Rapport
                                d’activité
                              </span>
                            )}
                        </div>

                        {challenge
                          ?.derniere_soumission && (
                          <div
                            className="dash-form-note"
                            style={{
                              marginBottom:
                                '14px',
                            }}
                          >
                            Dernière
                            soumission :{' '}
                            <strong>
                              {
                                challenge
                                  .derniere_soumission
                                  .statut
                              }
                            </strong>
                          </div>
                        )}

                        <button
                          type="button"
                          className={
                            isLocked
                              ? 'dash-secondary-btn'
                              : 'dash-primary-btn'
                          }
                          disabled={isLocked}
                          onClick={() =>
                            handleChallengeAction(
                              challenge
                            )
                          }
                        >
                          {getButtonLabel(
                            challenge
                          )}
                        </button>
                      </div>
                    </article>
                  )
                }
              )}
            </div>

            {/* PAGINATION */}

            {totalPages > 1 && (
              <div
                className="dash-actions-row"
                style={{
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexWrap: 'wrap',
                  marginTop: '10px',
                }}
              >
                <button
                  type="button"
                  className="dash-light-btn"
                  disabled={
                    currentPage === 1
                  }
                  onClick={() =>
                    handlePageChange(
                      currentPage - 1
                    )
                  }
                >
                  ← {labels.previous}
                </button>

                {visiblePages[0] > 1 && (
                  <>
                    <button
                      type="button"
                      className="dash-light-btn"
                      onClick={() =>
                        handlePageChange(1)
                      }
                    >
                      1
                    </button>

                    {visiblePages[0] > 2 && (
                      <span className="dash-pill">
                        …
                      </span>
                    )}
                  </>
                )}

                {visiblePages.map(
                  (page) => (
                    <button
                      key={page}
                      type="button"
                      className={
                        currentPage === page
                          ? 'dash-primary-btn'
                          : 'dash-light-btn'
                      }
                      aria-current={
                        currentPage === page
                          ? 'page'
                          : undefined
                      }
                      onClick={() =>
                        handlePageChange(
                          page
                        )
                      }
                    >
                      {page}
                    </button>
                  )
                )}

                {visiblePages[
                  visiblePages.length - 1
                ] < totalPages && (
                  <>
                    {visiblePages[
                      visiblePages.length - 1
                    ] < totalPages - 1 && (
                      <span className="dash-pill">
                        …
                      </span>
                    )}

                    <button
                      type="button"
                      className="dash-light-btn"
                      onClick={() =>
                        handlePageChange(
                          totalPages
                        )
                      }
                    >
                      {totalPages}
                    </button>
                  </>
                )}

                <button
                  type="button"
                  className="dash-light-btn"
                  disabled={
                    currentPage ===
                    totalPages
                  }
                  onClick={() =>
                    handlePageChange(
                      currentPage + 1
                    )
                  }
                >
                  {labels.next} →
                </button>
              </div>
            )}

            <p
              className="dash-form-note"
              style={{
                margin: 0,
                textAlign: 'center',
              }}
            >
              Affichage de{' '}
              {firstDisplayedItem} à{' '}
              {lastDisplayedItem} sur{' '}
              {filteredChallenges.length}{' '}
              défi
              {filteredChallenges.length > 1
                ? 's'
                : ''}
            </p>
          </>
        )}
    </section>
  )
}

export default ChallengesSection