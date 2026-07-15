import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'

import api from '../../api/api'
import { getCookie } from '../../utils/cookies'

import './ChallengesSection.css'

const ENDPOINT = '/challenges/defis/'
const CHALLENGES_PER_PAGE = 4

const STORAGE_KEYS = {
  SELECTED_CHALLENGE:
    'waterChallengeSelectedChallenge',

  CURRENT_CHALLENGE:
    'waterChallengeCurrentChallenge',

  CHALLENGE_MODULE:
    'waterChallengeChallengeModule',

  CHALLENGE_MODULE_ID:
    'waterChallengeChallengeModuleId',

  CHALLENGE_MODULE_SLUG:
    'waterChallengeChallengeModuleSlug',
}

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
    challenge?.module_detail?.title ??
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
        STORAGE_KEYS.CHALLENGE_MODULE
      )

    if (!storedValue) {
      return null
    }

    const parsedValue =
      JSON.parse(storedValue)

    return (
      parsedValue &&
      typeof parsedValue === 'object'
        ? parsedValue
        : null
    )
  } catch (storageError) {
    console.error(
      'Impossible de lire le module enregistré :',
      storageError
    )

    return null
  }
}

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

  if (!urlModuleId && !urlModuleSlug) {
    return emptyFilter
  }

  const storedModule = readStoredModule()

  const storedModuleId =
    normalizeIdentifier(
      storedModule?.id ||
      sessionStorage.getItem(
        STORAGE_KEYS.CHALLENGE_MODULE_ID
      )
    )

  const storedModuleSlug =
    normalizeIdentifier(
      storedModule?.slug ||
      sessionStorage.getItem(
        STORAGE_KEYS.CHALLENGE_MODULE_SLUG
      )
    )

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
        ? String(
            storedModule?.titre ||
            storedModule?.title ||
            ''
          ).trim()
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
    // La valeur n'est pas du JSON.
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

/*
 * Aucun état verrouillé n'est créé ici.
 * Tous les challenges restent accessibles,
 * indépendamment des informations d'accès du backend.
 */
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
    challenge?.termine_le ||
    completedStatuses.includes(status) ||
    completedStatuses.includes(
      submissionStatus
    )
  ) {
    return {
      key: 'completed',
      label: 'Déjà réalisé',
      icon: '✅',
    }
  }

  if (
    challenge?.a_soumission_en_attente ||
    pendingStatuses.includes(
      submissionStatus
    )
  ) {
    return {
      key: 'pending',
      label: 'Soumission en attente',
      icon: '⏳',
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
    }
  }

  if (
    challenge?.commence_le ||
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
    }
  }

  return {
    key: 'available',
    label: 'Disponible',
    icon: '🏆',
  }
}

const getVisiblePages = (
  currentPage,
  totalPages
) => {
  if (totalPages <= 5) {
    return Array.from(
      { length: totalPages },
      (_, index) => index + 1
    )
  }

  let startPage = currentPage - 2
  let endPage = currentPage + 2

  if (startPage < 1) {
    startPage = 1
    endPage = 5
  }

  if (endPage > totalPages) {
    endPage = totalPages
    startPage = totalPages - 4
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
    selectedChallenge,
    setSelectedChallenge,
  ] = useState(null)

  const [
    isLoading,
    setIsLoading,
  ] = useState(true)

  const [error, setError] =
    useState('')

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
      title:
        t?.challenges?.title ||
        'Challenges',

      subtitle:
        t?.challenges?.subtitle ||
        'Réalise des actions concrètes et partage les preuves de ton activité.',

      objective:
        t?.challenges?.objective ||
        'Objectif',

      expectedResult:
        'Résultat attendu',

      instructions:
        t?.challenges?.instructions ||
        'Critères de validation',

      requiredProofs:
        'Preuves demandées',

      retry: 'Réessayer',
      previous: 'Précédent',
      next: 'Suivant',

      empty:
        'Aucun challenge disponible pour le moment.',
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
            'Impossible de récupérer les challenges.'
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
                firstChallenge?.ordre ??
                  0
              ) -
              Number(
                secondChallenge?.ordre ??
                  0
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
          'Erreur de récupération des challenges :',
          requestError
        )

        const responseData =
          requestError
            ?.response
            ?.data

        setError(
          responseData?.erreur ||
          responseData?.detail ||
          responseData?.message ||
          requestError?.message ||
          'Impossible de charger les challenges.'
        )

        setChallenges([])
        setCurrentPage(1)
      } finally {
        setIsLoading(false)
      }
    }, [])

  useEffect(() => {
    loadChallenges()
  }, [loadChallenges])

  /* =======================================================
     SYNCHRONISATION URL / NAVIGATEUR
     ======================================================= */

  useEffect(() => {
    const handlePopState = () => {
      const searchParams =
        new URLSearchParams(
          window.location.search
        )

      setModuleFilter(
        getModuleFilterFromLocation()
      )

      const challengeId =
        normalizeIdentifier(
          searchParams.get(
            'challengeId'
          )
        )

      if (!challengeId) {
        setSelectedChallenge(null)
        return
      }

      const matchingChallenge =
        challenges.find(
          (challenge) =>
            normalizeIdentifier(
              challenge?.id
            ) === challengeId
        )

      setSelectedChallenge(
        matchingChallenge || null
      )
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
  }, [challenges])

  /*
   * Restaure le détail après un rechargement
   * si challengeId est présent dans l'URL.
   */
  useEffect(() => {
    if (
      isLoading ||
      challenges.length === 0 ||
      selectedChallenge
    ) {
      return
    }

    const searchParams =
      new URLSearchParams(
        window.location.search
      )

    const challengeId =
      normalizeIdentifier(
        searchParams.get(
          'challengeId'
        )
      )

    if (!challengeId) {
      return
    }

    const matchingChallenge =
      challenges.find(
        (challenge) =>
          normalizeIdentifier(
            challenge?.id
          ) === challengeId
      )

    if (matchingChallenge) {
      setSelectedChallenge(
        matchingChallenge
      )
    }
  }, [
    challenges,
    isLoading,
    selectedChallenge,
  ])

  /* =======================================================
     FILTRAGE PAR MODULE
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

          return matchesId || matchesSlug
        }
      )
    }, [
      challenges,
      moduleFilter,
    ])

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

  const totalPages = useMemo(() => {
    return Math.max(
      1,
      Math.ceil(
        filteredChallenges.length /
          CHALLENGES_PER_PAGE
      )
    )
  }, [filteredChallenges.length])

  const paginatedChallenges =
    useMemo(() => {
      const startIndex =
        (
          currentPage - 1
        ) * CHALLENGES_PER_PAGE

      return filteredChallenges.slice(
        startIndex,
        startIndex +
          CHALLENGES_PER_PAGE
      )
    }, [
      currentPage,
      filteredChallenges,
    ])

  const visiblePages = useMemo(() => {
    return getVisiblePages(
      currentPage,
      totalPages
    )
  }, [currentPage, totalPages])

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages)
    }
  }, [currentPage, totalPages])

  const firstDisplayedItem =
    filteredChallenges.length === 0
      ? 0
      : (
          currentPage - 1
        ) *
          CHALLENGES_PER_PAGE +
        1

  const lastDisplayedItem =
    Math.min(
      currentPage *
        CHALLENGES_PER_PAGE,
      filteredChallenges.length
    )

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
      [currentPage, totalPages]
    )

  /* =======================================================
     MODULE : VOIR TOUS LES CHALLENGES
     ======================================================= */

  const handleShowAllChallenges =
    useCallback(() => {
      const nextUrl = new URL(
        window.location.href
      )

      const parametersToDelete = [
        'module',
        'moduleId',
        'moduleSlug',
        'module_slug',
        'slug',
        'challengeId',
        'view',
      ]

      parametersToDelete.forEach(
        (parameterName) => {
          nextUrl.searchParams.delete(
            parameterName
          )
        }
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
          STORAGE_KEYS.CHALLENGE_MODULE
        )

        sessionStorage.removeItem(
          STORAGE_KEYS.CHALLENGE_MODULE_ID
        )

        sessionStorage.removeItem(
          STORAGE_KEYS.CHALLENGE_MODULE_SLUG
        )
      } catch (storageError) {
        console.error(
          'Impossible de nettoyer le module :',
          storageError
        )
      }

      setSelectedChallenge(null)

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
     SÉLECTION ET DÉTAIL DU CHALLENGE
     ======================================================= */

  const saveSelectedChallenge =
    useCallback((challenge) => {
      const selectedValue = {
        ...challenge,

        selectedAt:
          new Date().toISOString(),
      }

      try {
        sessionStorage.setItem(
          STORAGE_KEYS.SELECTED_CHALLENGE,
          JSON.stringify(selectedValue)
        )

        sessionStorage.setItem(
          STORAGE_KEYS.CURRENT_CHALLENGE,
          JSON.stringify(selectedValue)
        )
      } catch (storageError) {
        console.error(
          'Impossible d’enregistrer le challenge :',
          storageError
        )
      }
    }, [])

  const openChallengeDetails =
    useCallback(
      (challenge) => {
        saveSelectedChallenge(challenge)
        setSelectedChallenge(challenge)

        const nextUrl = new URL(
          window.location.href
        )

        nextUrl.searchParams.set(
          'section',
          'challenges'
        )

        nextUrl.searchParams.set(
          'challengeId',
          normalizeIdentifier(
            challenge?.id
          )
        )

        window.history.pushState(
          {
            ...(window.history.state || {}),
            section: 'challenges',
            challengeId: challenge?.id,
          },
          '',
          nextUrl
        )

        window.scrollTo({
          top: 0,
          behavior: 'smooth',
        })
      },
      [saveSelectedChallenge]
    )

  const closeChallengeDetails =
    useCallback(() => {
      setSelectedChallenge(null)

      const nextUrl = new URL(
        window.location.href
      )

      nextUrl.searchParams.delete(
        'challengeId'
      )

      window.history.pushState(
        {
          ...(window.history.state || {}),
          section: 'challenges',
        },
        '',
        nextUrl
      )

      window.scrollTo({
        top: 0,
        behavior: 'smooth',
      })
    }, [])

  const continueToSubmission =
    useCallback(() => {
      if (!selectedChallenge) {
        return
      }

      saveSelectedChallenge(
        selectedChallenge
      )

      if (
        typeof setActiveSection ===
        'function'
      ) {
        setActiveSection('submit')
      }
    }, [
      saveSelectedChallenge,
      selectedChallenge,
      setActiveSection,
    ])

  /* =======================================================
     AFFICHAGE DU DÉTAIL
     ======================================================= */

  if (selectedChallenge) {
    const state = getChallengeState(
      selectedChallenge
    )

    const criteria = parseCriteria(
      selectedChallenge
        ?.criteres_validation
    )

    const minimumPhotos = Number(
      selectedChallenge
        ?.nombre_photos_min ??
        0
    )

    const maximumPhotos = Number(
      selectedChallenge
        ?.nombre_photos_max ??
        0
    )

    const challengeModuleTitle =
      getChallengeModuleTitle(
        selectedChallenge
      ) ||
      currentModuleLabel ||
      'Water Challenge'

    return (
      <section className="challenges-page challenge-details">
        <div className="challenge-details__navigation">
          <button
            type="button"
            className="challenge-details__back"
            onClick={
              closeChallengeDetails
            }
          >
            <span aria-hidden="true">
              ←
            </span>

            Retour aux challenges
          </button>
        </div>

        <article className="challenge-details__card">
          <div className="challenge-details__hero">
            <span
              className={[
                'challenge-card__status',
                `challenge-card__status--${state.key}`,
              ].join(' ')}
            >
              {state.icon}{' '}
              {state.label}
            </span>

            <div className="challenge-details__hero-content">
              <p>
                📚 {challengeModuleTitle}
              </p>

              <h1>
                {selectedChallenge?.titre ||
                  'Challenge'}
              </h1>

              <div className="challenge-details__hero-meta">
                <span>
                  🎯{' '}
                  {formatLevel(
                    selectedChallenge
                      ?.niveau
                  )}
                </span>

                {selectedChallenge
                  ?.duree_estimee && (
                  <span>
                    ⏱️{' '}
                    {
                      selectedChallenge
                        .duree_estimee
                    }
                  </span>
                )}

                <span>
                  ⭐{' '}
                  {Number(
                    selectedChallenge
                      ?.points_recompense ??
                    selectedChallenge
                      ?.points ??
                    0
                  )}{' '}
                  points
                </span>
              </div>
            </div>
          </div>

          <div className="challenge-details__body">
            <section className="challenge-details__section">
              <span className="challenge-details__section-icon">
                🎯
              </span>

              <div>
                <h2>{labels.objective}</h2>

                <p>
                  {selectedChallenge
                    ?.description ||
                    'Réalisez le challenge en respectant les consignes indiquées.'}
                </p>
              </div>
            </section>

            {selectedChallenge
              ?.resultat_attendu && (
              <section className="challenge-details__section">
                <span className="challenge-details__section-icon">
                  ✅
                </span>

                <div>
                  <h2>
                    {labels.expectedResult}
                  </h2>

                  <p>
                    {
                      selectedChallenge
                        .resultat_attendu
                    }
                  </p>
                </div>
              </section>
            )}

            {criteria.length > 0 && (
              <section className="challenge-details__section">
                <span className="challenge-details__section-icon">
                  📋
                </span>

                <div>
                  <h2>
                    {labels.instructions}
                  </h2>

                  <ul className="challenge-details__criteria">
                    {criteria.map(
                      (
                        criterion,
                        criterionIndex
                      ) => (
                        <li
                          key={`${selectedChallenge.id}-criterion-${criterionIndex}`}
                        >
                          <span>✓</span>
                          {criterion}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              </section>
            )}

            <section className="challenge-details__section">
              <span className="challenge-details__section-icon">
                📎
              </span>

              <div>
                <h2>
                  {labels.requiredProofs}
                </h2>

                <div className="challenge-details__proofs">
                  {minimumPhotos > 0 && (
                    <span>
                      📷 Minimum{' '}
                      {minimumPhotos}{' '}
                      photo
                      {minimumPhotos > 1
                        ? 's'
                        : ''}
                    </span>
                  )}

                  {maximumPhotos > 0 && (
                    <span>
                      🖼️ Maximum{' '}
                      {maximumPhotos}{' '}
                      photo
                      {maximumPhotos > 1
                        ? 's'
                        : ''}
                    </span>
                  )}

                  {selectedChallenge
                    ?.video_obligatoire && (
                    <span>
                      🎥 Vidéo demandée
                    </span>
                  )}

                  {minimumPhotos === 0 &&
                    maximumPhotos === 0 &&
                    !selectedChallenge
                      ?.video_obligatoire && (
                      <span>
                        📄 Rapport d’activité
                      </span>
                    )}
                </div>
              </div>
            </section>

            {selectedChallenge
              ?.derniere_soumission && (
              <section className="challenge-details__submission">
                <span>
                  Dernière soumission
                </span>

                <strong>
                  {
                    selectedChallenge
                      .derniere_soumission
                      .statut
                  }
                </strong>
              </section>
            )}

            <div className="challenge-details__notice">
              <span aria-hidden="true">
                💡
              </span>

              <p>
                Ce challenge peut être réalisé
                ou soumis à nouveau à tout moment.
              </p>
            </div>

            <div className="challenge-details__actions">
              <button
                type="button"
                className="challenge-details__secondary"
                onClick={
                  closeChallengeDetails
                }
              >
                Retour
              </button>

              <button
                type="button"
                className="challenge-details__primary"
                onClick={
                  continueToSubmission
                }
              >
                <span>
                  Soumettre une activité
                </span>

                <span aria-hidden="true">
                  →
                </span>
              </button>
            </div>
          </div>
        </article>
      </section>
    )
  }

  /* =======================================================
     AFFICHAGE DE LA LISTE
     ======================================================= */

  return (
    <section className="challenges-page">
      <div className="challenges-page__header">
        <div>
          <h1 className="challenges-page__title">
            {labels.title}
          </h1>

          <p className="challenges-page__subtitle">
            {moduleFilter.isActive
              ? `Challenges associés au module ${currentModuleLabel}.`
              : labels.subtitle}
          </p>
        </div>

        {!isLoading && !error && (
          <span className="challenges-page__count">
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
          <div className="challenge-module-filter">
            <span>
              📚 Challenges du module{' '}
              <strong>
                {currentModuleLabel}
              </strong>
            </span>

            <button
              type="button"
              onClick={
                handleShowAllChallenges
              }
            >
              Voir tous les challenges
            </button>
          </div>
        )}

      {isLoading && (
        <div className="challenges-page__grid">
          {[1, 2, 3, 4].map(
            (item) => (
              <article
                className="challenge-card challenge-card--skeleton"
                key={item}
              >
                <div className="challenge-card__body">
                  <span className="challenge-skeleton challenge-skeleton--pill" />
                  <span className="challenge-skeleton challenge-skeleton--title" />
                  <span className="challenge-skeleton" />
                  <span className="challenge-skeleton challenge-skeleton--short" />
                  <span className="challenge-skeleton challenge-skeleton--button" />
                </div>
              </article>
            )
          )}
        </div>
      )}

      {!isLoading && error && (
        <div className="challenges-page__error">
          <span aria-hidden="true">
            ⚠️
          </span>

          <div>
            <h2>
              Impossible de charger les challenges
            </h2>

            <p>{error}</p>
          </div>

          <button
            type="button"
            onClick={loadChallenges}
          >
            {labels.retry}
          </button>
        </div>
      )}

      {!isLoading &&
        !error &&
        filteredChallenges.length === 0 && (
          <div className="challenges-page__empty">
            <span aria-hidden="true">
              🏆
            </span>

            <p>
              {moduleFilter.isActive
                ? `Aucun challenge n’est associé au module ${currentModuleLabel}.`
                : labels.empty}
            </p>

            {moduleFilter.isActive && (
              <button
                type="button"
                className="challenge-details__secondary"
                onClick={
                  handleShowAllChallenges
                }
              >
                Afficher tous les challenges
              </button>
            )}
          </div>
        )}

      {!isLoading &&
        !error &&
        filteredChallenges.length > 0 && (
          <>
            <div className="challenges-page__grid">
              {paginatedChallenges.map(
                (
                  challenge,
                  challengeIndex
                ) => {
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

                  const challengeModuleTitle =
                    getChallengeModuleTitle(
                      challenge
                    ) ||
                    currentModuleLabel ||
                    'Water Challenge'

                  const challengeNumber =
                    (
                      currentPage - 1
                    ) *
                      CHALLENGES_PER_PAGE +
                    challengeIndex +
                    1

                  return (
                    <article
                      className={[
                        'challenge-card',
                        `challenge-card--${state.key}`,
                        moduleFilter.isActive
                          ? 'challenge-card--selected-module'
                          : '',
                      ]
                        .filter(Boolean)
                        .join(' ')}
                      key={
                        challenge?.id ??
                        challengeNumber
                      }
                    >
                      <div className="challenge-card__body">
                        <div className="challenge-card__topline">
                          <span className="challenge-card__number">
                            Défi {challengeNumber}
                          </span>

                          <span
                            className={[
                              'challenge-card__status',
                              `challenge-card__status--${state.key}`,
                            ].join(' ')}
                          >
                            {state.icon}{' '}
                            {state.label}
                          </span>
                        </div>

                        <div className="challenge-card__meta">
                          <span className="challenge-card__level">
                            🎯{' '}
                            {formatLevel(
                              challenge?.niveau
                            )}
                          </span>

                          <span className="challenge-card__points">
                            ⭐{' '}
                            {Number(
                              challenge
                                ?.points_recompense ??
                              challenge?.points ??
                              0
                            )}{' '}
                            pts
                          </span>
                        </div>

                        <p className="challenge-card__module">
                          📚 {challengeModuleTitle}
                        </p>

                        <h2>
                          {challenge?.titre ||
                            'Challenge'}
                        </h2>

                        <p className="challenge-card__description">
                          {challenge?.description ||
                            'Consultez les détails du challenge avant de soumettre votre activité.'}
                        </p>

                        <div className="challenge-card__quick-info">
                          <span>
                            <strong>⏱️</strong>
                            <small>Durée</small>
                            <b>
                              {challenge
                                ?.duree_estimee ||
                                'Libre'}
                            </b>
                          </span>

                          <span>
                            <strong>📋</strong>
                            <small>Critères</small>
                            <b>{criteria.length}</b>
                          </span>

                          <span>
                            <strong>📷</strong>
                            <small>Photos</small>
                            <b>
                              {minimumPhotos > 0
                                ? minimumPhotos
                                : '—'}
                            </b>
                          </span>
                        </div>

                        <button
                          type="button"
                          className="challenge-card__action"
                          onClick={() =>
                            openChallengeDetails(
                              challenge
                            )
                          }
                        >
                          <span>
                            Voir le challenge
                          </span>

                          <span aria-hidden="true">
                            →
                          </span>
                        </button>
                      </div>
                    </article>
                  )
                }
              )}
            </div>

            {totalPages > 1 && (
              <div className="challenge-pagination">
                <button
                  type="button"
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

                {visiblePages.map(
                  (page) => (
                    <button
                      key={page}
                      type="button"
                      className={
                        currentPage === page
                          ? 'is-active'
                          : ''
                      }
                      aria-current={
                        currentPage === page
                          ? 'page'
                          : undefined
                      }
                      onClick={() =>
                        handlePageChange(page)
                      }
                    >
                      {page}
                    </button>
                  )
                )}

                <button
                  type="button"
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

            <p className="challenges-page__result-count">
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