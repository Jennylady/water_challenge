import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'

import { getMediaUrl as resolveMediaUrl } from '../../api/api'
import { formationApi } from '../../api/services'
import {
  buildDashboardUrl,
  parseDashboardLocation,
} from '../../utils/dashboardRoutes'

import Read from './Read'
import Quiz from './Quiz'

import './LearningSection.css'

const MODULE_TARGETS = {
  READ: 'read',
  QUIZ: 'quiz',
  CHALLENGE: 'challenge',
}

const MODULE_VIEWS = {
  CATALOG: 'catalog',
  READ: 'read',
  QUIZ: 'quiz',
}

const getModulesPerPage = () => {
  if (typeof window === 'undefined') {
    return 3
  }

  if (window.innerWidth <= 760) {
    return 1
  }

  if (window.innerWidth <= 1180) {
    return 2
  }

  return 3
}

const STORAGE_KEYS = {
  BOOKMARKS:
    'waterChallengeBookmarkedModules',

  SELECTED_MODULE:
    'waterChallengeSelectedModule',

  CURRENT_MODULE:
    'waterChallengeCurrentModule',

  MODULE_TARGET:
    'waterChallengeModuleTarget',

  MODULE_NAVIGATION:
    'waterChallengeModuleNavigation',

  CHALLENGE_MODULE:
    'waterChallengeChallengeModule',

  CHALLENGE_MODULE_ID:
    'waterChallengeChallengeModuleId',

  CHALLENGE_MODULE_SLUG:
    'waterChallengeChallengeModuleSlug',
}



const getModuleSlug = (module) => {
  return String(module?.slug || '').trim()
}

const isModuleAccessible = (module) => {

  return module?.est_accessible !== false
}

const getModuleDisplayOrder = (
  module,
  moduleIndex
) => {
  const receivedOrder =
    Number(module?.ordre)

  /*
   * Si le backend commence à 0,
   * on utilise la position visuelle.
   */
  if (
    Number.isFinite(receivedOrder) &&
    receivedOrder > 0
  ) {
    return receivedOrder
  }

  return moduleIndex + 1
}

const getLessonsCount = (module) => {
  const receivedCount =
    module?.nombre_lecons ??
    module?.lecons_count ??
    module?.lessons_count

  if (
    receivedCount !== undefined &&
    receivedCount !== null
  ) {
    return receivedCount
  }

  if (Array.isArray(module?.lecons)) {
    return module.lecons.length
  }

  if (Array.isArray(module?.lessons)) {
    return module.lessons.length
  }

  /*
   * Le backend actuel retourne directement
   * module.contenu. Cela représente une leçon.
   */
  if (
    module?.contenu ||
    module?.video ||
    (
      Array.isArray(
        module?.illustrations
      ) &&
      module.illustrations.length > 0
    )
  ) {
    return 1
  }

  return '—'
}

const getQuestionsCount = (module) => {
  const receivedCount =
    module?.nombre_questions ??
    module?.questions_count ??
    module?.quiz_questions_count

  if (
    receivedCount !== undefined &&
    receivedCount !== null
  ) {
    return receivedCount
  }

  const questions =
    module?.quiz?.questions ??
    module?.questions ??
    module?.quiz_questions

  if (Array.isArray(questions)) {
    return questions.length
  }

  return '—'
}

const getChallengeCount = (module) => {
  const receivedCount =
    module?.nombre_challenges ??
    module?.challenges_count ??
    module?.defis_count

  if (
    receivedCount !== undefined &&
    receivedCount !== null
  ) {
    return receivedCount
  }

  if (
    Array.isArray(module?.challenges)
  ) {
    return module.challenges.length
  }

  if (Array.isArray(module?.defis)) {
    return module.defis.length
  }

  return '—'
}

const getModuleProgress = (module) => {
  const receivedProgress =
    module?.progression?.pourcentage ??
    module?.progression ??
    module?.progress ??
    module?.pourcentage_progression

  const numericProgress = Number(receivedProgress)

  if (
    Number.isFinite(numericProgress)
  ) {
    return Math.min(
      100,
      Math.max(0, numericProgress)
    )
  }

  if (module?.est_termine) {
    return 100
  }

  if (module?.est_lu) {
    return 50
  }

  return 0
}

const readStoredBookmarks = () => {
  try {
    const storedValue =
      localStorage.getItem(
        STORAGE_KEYS.BOOKMARKS
      )

    if (!storedValue) {
      return []
    }

    const parsedValue =
      JSON.parse(storedValue)

    if (!Array.isArray(parsedValue)) {
      return []
    }

    return parsedValue.map(String)
  } catch {
    return []
  }
}

/* =========================================================
   COMPOSANT
   ========================================================= */

function LearningSection({
  setActiveSection,
}) {
  const [
    modules,
    setModules,
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
    actionError,
    setActionError,
  ] = useState('')

  const [
    openingAction,
    setOpeningAction,
  ] = useState('')

  const [
    activeView,
    setActiveView,
  ] = useState(
    MODULE_VIEWS.CATALOG
  )

  const [
    selectedModule,
    setSelectedModule,
  ] = useState(null)

  const [
    currentPage,
    setCurrentPage,
  ] = useState(1)

  const [
    modulesPerPage,
    setModulesPerPage,
  ] = useState(
    getModulesPerPage
  )

  const [
    navigationVersion,
    setNavigationVersion,
  ] = useState(0)

  const [
    bookmarkedModules,
    setBookmarkedModules,
  ] = useState(
    readStoredBookmarks
  )

  const gridRef = useRef(null)

  const mobileSwipeRef = useRef({
    pointerId: null,
    startX: 0,
    startScrollLeft: 0,
    moved: false,
  })

  const suppressGridClickRef =
    useRef(false)

  const restoredModuleRef =
    useRef('')

  const labels = useMemo(
    () => ({
      kicker: 'Formation',

      title:
        'Modules de formation',

      subtitle:
        'Découvrez les modules, consultez les leçons, passez les quiz et réalisez les challenges.',

      module: 'Module',
      modules: 'modules',

      beginner: 'Débutant',

      available: 'Accessible',
      inProgress: 'En cours',
      completed: 'Terminé',
      locked: 'Verrouillé',

      read: 'Lecture',
      quiz: 'Quiz',
      challenge: 'Challenge',

      lessons: 'leçons',
      questions: 'questions',
      challenges: 'challenges',

      start: 'Commencer',
      continue: 'Continuer',
      restart: 'Revoir',

      details: 'Voir les détails',
      opening: 'Ouverture...',

      empty:
        'Aucun module de formation disponible.',

      error:
        'Impossible de charger les modules.',

      retry: 'Réessayer',

      quizUnavailable:
        'Le quiz de ce module n’est pas encore disponible.',
    }),
    []
  )

  /* =======================================================
     URL DES MÉDIAS
     ======================================================= */

  const getMediaUrl = useCallback(
    (mediaPath) => resolveMediaUrl(mediaPath),
    []
  )

  /* =======================================================
     GESTION DES ERREURS
     ======================================================= */

  const getErrorMessage =
    useCallback(
      (requestError) => {
        const status =
          requestError?.response
            ?.status

        const responseData =
          requestError?.response
            ?.data

        if (
          !requestError?.response
        ) {
          return (
            requestError?.message ||
            'Impossible de contacter le serveur.'
          )
        }

        const backendMessage =
          responseData?.erreur ||
          responseData?.detail ||
          responseData?.message

        if (status === 401) {
          return (
            backendMessage ||
            'Votre session a expiré. Veuillez vous reconnecter.'
          )
        }

        if (status === 403) {
          return (
            backendMessage ||
            "Vous n'avez pas accès à ce module."
          )
        }

        if (status === 404) {
          return (
            backendMessage ||
            "Le module demandé n'existe pas."
          )
        }

        if (status >= 500) {
          return (
            backendMessage ||
            'Le serveur rencontre actuellement un problème.'
          )
        }

        if (
          typeof responseData ===
          'string'
        ) {
          return responseData
        }

        return (
          backendMessage ||
          requestError?.message ||
          labels.error
        )
      },
      [labels.error]
    )

  /* =======================================================
     CHARGEMENT DE LA LISTE
     ======================================================= */

  const loadModules =
    useCallback(async () => {
      setIsLoading(true)
      setError('')
      setActionError('')

      try {
        const receivedModules =
          await formationApi.listModules()

        if (!Array.isArray(receivedModules)) {
          throw new Error(
            'Le serveur ne retourne pas une liste de modules valide.'
          )
        }

        setModules(receivedModules)
      } catch (requestError) {
        console.error(
          'Erreur pendant la récupération des modules :',
          requestError
        )

        setModules([])
        setError(getErrorMessage(requestError))
      } finally {
        setIsLoading(false)
      }
    }, [getErrorMessage])

  useEffect(() => {
    loadModules()
  }, [loadModules])

  const sortedModules =
    useMemo(() => {
      return [...modules].sort(
        (
          firstModule,
          secondModule
        ) => {
          return (
            Number(
              firstModule?.ordre ??
                0
            ) -
            Number(
              secondModule?.ordre ??
                0
            )
          )
        }
      )
    }, [modules])


  const totalPages = useMemo(
    () =>
      Math.max(
        1,
        Math.ceil(
          sortedModules.length /
            modulesPerPage
        )
      ),
    [
      modulesPerPage,
      sortedModules.length,
    ]
  )

  const paginatedModules =
    useMemo(() => {
      /*
       * Sur mobile, tous les modules restent présents
       * dans la ligne afin de permettre le glissement
       * naturel vers le précédent ou le suivant.
       */
      if (modulesPerPage === 1) {
        return sortedModules
      }

      const startIndex =
        (currentPage - 1) *
        modulesPerPage

      return sortedModules.slice(
        startIndex,
        startIndex +
          modulesPerPage
      )
    }, [
      currentPage,
      modulesPerPage,
      sortedModules,
    ])

  useEffect(() => {
    const handleResize = () => {
      const nextModulesPerPage =
        getModulesPerPage()

      setModulesPerPage(
        (currentValue) =>
          currentValue ===
          nextModulesPerPage
            ? currentValue
            : nextModulesPerPage
      )
    }

    window.addEventListener(
      'resize',
      handleResize
    )

    return () => {
      window.removeEventListener(
        'resize',
        handleResize
      )
    }
  }, [])

  useEffect(() => {
    setCurrentPage(
      (currentValue) =>
        Math.min(
          Math.max(1, currentValue),
          totalPages
        )
    )
  }, [totalPages])

  useEffect(() => {
    setCurrentPage(1)
  }, [modulesPerPage])

  const handlePageChange =
    useCallback(
      (nextPage) => {
        if (
          nextPage < 1 ||
          nextPage > totalPages ||
          nextPage === currentPage
        ) {
          return
        }

        setCurrentPage(nextPage)

        if (
          modulesPerPage === 1 &&
          gridRef.current
        ) {
          const targetCard =
            gridRef.current.children[
              nextPage - 1
            ]

          if (targetCard) {
            gridRef.current.scrollTo({
              left: targetCard.offsetLeft,
              behavior: 'smooth',
            })
          }

          return
        }

        window.scrollTo({
          top: 0,
          behavior: 'smooth',
        })
      },
      [
        currentPage,
        modulesPerPage,
        totalPages,
      ]
    )

  const handleMobileGridScroll =
    useCallback(() => {
      if (
        modulesPerPage !== 1 ||
        !gridRef.current
      ) {
        return
      }

      const gridNode =
        gridRef.current

      const cards = Array.from(
        gridNode.children
      )

      if (cards.length === 0) {
        return
      }

      let closestIndex = 0
      let closestDistance =
        Number.POSITIVE_INFINITY

      cards.forEach(
        (card, cardIndex) => {
          const distance =
            Math.abs(
              card.offsetLeft -
                gridNode.scrollLeft
            )

          if (
            distance <
            closestDistance
          ) {
            closestDistance =
              distance
            closestIndex =
              cardIndex
          }
        }
      )

      const visiblePage =
        closestIndex + 1

      setCurrentPage(
        (currentValue) =>
          currentValue === visiblePage
            ? currentValue
            : visiblePage
      )
    }, [modulesPerPage])


  const handleMobilePointerDown =
    useCallback(
      (event) => {
        if (
          modulesPerPage !== 1 ||
          !gridRef.current
        ) {
          return
        }

        if (
          event.pointerType === 'mouse' &&
          event.button !== 0
        ) {
          return
        }

        const gridNode =
          gridRef.current

        mobileSwipeRef.current = {
          pointerId: event.pointerId,
          startX: event.clientX,
          startScrollLeft:
            gridNode.scrollLeft,
          moved: false,
        }

        suppressGridClickRef.current =
          false

        try {
          gridNode.setPointerCapture(
            event.pointerId
          )
        } catch {
          // Certains navigateurs mobiles
          // gèrent déjà la capture du doigt.
        }
      },
      [modulesPerPage]
    )

  const handleMobilePointerMove =
    useCallback(
      (event) => {
        const swipeState =
          mobileSwipeRef.current

        if (
          modulesPerPage !== 1 ||
          !gridRef.current ||
          swipeState.pointerId !==
            event.pointerId
        ) {
          return
        }

        const deltaX =
          event.clientX -
          swipeState.startX

        if (Math.abs(deltaX) > 5) {
          swipeState.moved = true
          suppressGridClickRef.current =
            true
        }

        gridRef.current.scrollLeft =
          swipeState.startScrollLeft -
          deltaX

        if (Math.abs(deltaX) > 8) {
          event.preventDefault()
        }
      },
      [modulesPerPage]
    )

  const finishMobileSwipe =
    useCallback(
      (event, wasCancelled = false) => {
        const swipeState =
          mobileSwipeRef.current

        if (
          modulesPerPage !== 1 ||
          !gridRef.current ||
          swipeState.pointerId !==
            event.pointerId
        ) {
          return
        }

        const gridNode =
          gridRef.current

        const deltaX =
          event.clientX -
          swipeState.startX

        const threshold = Math.max(
          42,
          gridNode.clientWidth * 0.12
        )

        let nextPage = currentPage

        if (!wasCancelled) {
          if (deltaX > threshold) {
            nextPage = Math.max(
              1,
              currentPage - 1
            )
          } else if (
            deltaX < -threshold
          ) {
            nextPage = Math.min(
              totalPages,
              currentPage + 1
            )
          } else {
            const cards = Array.from(
              gridNode.children
            )

            let closestIndex =
              currentPage - 1
            let closestDistance =
              Number.POSITIVE_INFINITY

            cards.forEach(
              (card, cardIndex) => {
                const distance = Math.abs(
                  card.offsetLeft -
                    gridNode.scrollLeft
                )

                if (
                  distance <
                  closestDistance
                ) {
                  closestDistance =
                    distance
                  closestIndex =
                    cardIndex
                }
              }
            )

            nextPage =
              closestIndex + 1
          }
        }

        try {
          gridNode.releasePointerCapture(
            event.pointerId
          )
        } catch {
          // La capture peut déjà être libérée.
        }

        mobileSwipeRef.current = {
          pointerId: null,
          startX: 0,
          startScrollLeft: 0,
          moved: false,
        }

        if (nextPage !== currentPage) {
          handlePageChange(nextPage)
        } else {
          const currentCard =
            gridNode.children[
              currentPage - 1
            ]

          if (currentCard) {
            gridNode.scrollTo({
              left: currentCard.offsetLeft,
              behavior: 'smooth',
            })
          }
        }

        window.setTimeout(() => {
          suppressGridClickRef.current =
            false
        }, 120)
      },
      [
        currentPage,
        handlePageChange,
        modulesPerPage,
        totalPages,
      ]
    )

  const handleMobilePointerUp =
    useCallback(
      (event) => {
        finishMobileSwipe(event, false)
      },
      [finishMobileSwipe]
    )

  const handleMobilePointerCancel =
    useCallback(
      (event) => {
        finishMobileSwipe(event, true)
      },
      [finishMobileSwipe]
    )

  const handleMobileGridClickCapture =
    useCallback((event) => {
      if (
        suppressGridClickRef.current
      ) {
        event.preventDefault()
        event.stopPropagation()
      }
    }, [])

  useEffect(() => {
    if (
      modulesPerPage !== 1 ||
      !gridRef.current
    ) {
      return
    }

    const targetCard =
      gridRef.current.children[
        currentPage - 1
      ]

    if (targetCard) {
      gridRef.current.scrollTo({
        left: targetCard.offsetLeft,
        behavior: 'auto',
      })
    }
  }, [
    currentPage,
    modulesPerPage,
  ])

  /* =======================================================
     STATUT D’UN MODULE
     ======================================================= */

  const getModuleStatus =
    useCallback(
      (module) => {
        const progress =
          getModuleProgress(module)

        if (module?.est_termine) {
          return {
            key: 'completed',
            label:
              labels.completed,
            icon: '✓',
            progress: 100,
          }
        }

        if (
          !isModuleAccessible(module)
        ) {
          return {
            key: 'locked',
            label: labels.locked,
            icon: '🔒',
            progress: 0,
          }
        }

        if (
          module?.est_lu ||
          progress > 0
        ) {
          return {
            key: 'read',
            label:
              labels.inProgress,
            icon: '📖',
            progress,
          }
        }

        return {
          key: 'available',
          label:
            labels.available,
          icon: '▶',
          progress,
        }
      },
      [labels]
    )

  /* =======================================================
     DATE DU MODULE
     ======================================================= */

  const formatModulePeriod =
    useCallback((module) => {
      if (
        !module?.date_debut &&
        !module?.date_fin
      ) {
        return ''
      }

      const formatter =
        new Intl.DateTimeFormat(
          'fr-FR',
          {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
          }
        )

      const startDate =
        module?.date_debut
          ? new Date(
              module.date_debut
            )
          : null

      const endDate =
        module?.date_fin
          ? new Date(
              module.date_fin
            )
          : null

      const validStart =
        startDate &&
        !Number.isNaN(
          startDate.getTime()
        )

      const validEnd =
        endDate &&
        !Number.isNaN(
          endDate.getTime()
        )

      if (
        validStart &&
        validEnd
      ) {
        return `${formatter.format(
          startDate
        )} — ${formatter.format(
          endDate
        )}`
      }

      if (validStart) {
        return formatter.format(
          startDate
        )
      }

      if (validEnd) {
        return formatter.format(
          endDate
        )
      }

      return ''
    }, [])

  /* =======================================================
     CHARGEMENT DU DÉTAIL
     ======================================================= */

  const fetchModuleDetail =
    useCallback(async (moduleSlug) => {
      const normalizedSlug = String(moduleSlug || '').trim()

      if (!normalizedSlug) {
        throw new Error(
          'Impossible d’identifier le module demandé.'
        )
      }

      const moduleDetail =
        await formationApi.getModule(normalizedSlug)

      if (!moduleDetail?.slug) {
        throw new Error(
          'Le serveur ne retourne pas un module valide.'
        )
      }

      if (!isModuleAccessible(moduleDetail)) {
        throw new Error(
          "Ce module n'est pas encore accessible."
        )
      }

      return moduleDetail
    }, [])

  /* =======================================================
     SAUVEGARDE DU MODULE
     ======================================================= */

  const saveModuleNavigation =
    useCallback(
      (
        moduleDetail,
        target
      ) => {
        const moduleSlug =
          getModuleSlug(
            moduleDetail
          )

        const navigationData = {
          moduleSlug,

          target,

          savedAt:
            new Date().toISOString(),
        }

        try {
          sessionStorage.setItem(
            STORAGE_KEYS
              .SELECTED_MODULE,

            JSON.stringify(
              moduleDetail
            )
          )

          sessionStorage.setItem(
            STORAGE_KEYS
              .CURRENT_MODULE,

            JSON.stringify(
              moduleDetail
            )
          )

          sessionStorage.setItem(
            STORAGE_KEYS
              .MODULE_TARGET,

            target
          )

          sessionStorage.setItem(
            STORAGE_KEYS
              .MODULE_NAVIGATION,

            JSON.stringify(
              navigationData
            )
          )
        } catch (storageError) {
          console.error(
            'Impossible d’enregistrer le module :',
            storageError
          )
        }
      },
      []
    )

  /* =======================================================
     URL DE LECTURE / QUIZ
     ======================================================= */

  const updateLearningUrl =
    useCallback(
      (
        moduleDetail,
        target,
        replace = false
      ) => {
        const moduleSlug =
          getModuleSlug(
            moduleDetail
          )

        if (!moduleSlug) {
          return
        }

        const historyState = {
          section: 'learning',
          moduleSlug,
          view: target,
        }

        const nextUrl = buildDashboardUrl({
          section: 'learning',
          moduleSlug,
          view:
            target === MODULE_TARGETS.QUIZ
              ? MODULE_TARGETS.QUIZ
              : MODULE_TARGETS.READ,
        })

        if (replace) {
          window.history.replaceState(historyState, '', nextUrl)
        } else {
          window.history.pushState(historyState, '', nextUrl)
        }
      },
      []
    )

  /* =======================================================
     OUVERTURE DE READ OU QUIZ
     ======================================================= */

  const openModuleView =
    useCallback(
      (
        moduleDetail,
        target,
        replaceUrl = false
      ) => {
        const nextView =
          target ===
          MODULE_TARGETS.QUIZ
            ? MODULE_VIEWS.QUIZ
            : MODULE_VIEWS.READ

        saveModuleNavigation(
          moduleDetail,
          target
        )

        setSelectedModule(
          moduleDetail
        )

        setActiveView(nextView)
        setActionError('')

        updateLearningUrl(
          moduleDetail,
          target,
          replaceUrl
        )

        window.scrollTo({
          top: 0,
          behavior: 'smooth',
        })
      },
      [
        saveModuleNavigation,
        updateLearningUrl,
      ]
    )

  /* =======================================================
     OUVERTURE DES CHALLENGES DU MODULE
     ======================================================= */

  const openChallengePage =
    useCallback(
      (moduleDetail, replaceUrl = false) => {
        const moduleSlug = getModuleSlug(moduleDetail)

        if (!moduleSlug) {
          setActionError(
            'Impossible d’identifier le module pour ouvrir ses challenges.'
          )
          return
        }

        try {
          sessionStorage.setItem(
            STORAGE_KEYS.CHALLENGE_MODULE_SLUG,
            moduleSlug
          )
          sessionStorage.removeItem(
            STORAGE_KEYS.CHALLENGE_MODULE_ID
          )
          sessionStorage.setItem(
            STORAGE_KEYS.CHALLENGE_MODULE,
            JSON.stringify(moduleDetail)
          )
        } catch (storageError) {
          console.error(
            'Impossible d’enregistrer le module des challenges :',
            storageError
          )
        }

        const nextUrl = buildDashboardUrl({
          section: 'challenges',
          moduleSlug,
        })

        const historyState = {
          section: 'challenges',
          moduleSlug,
        }

        if (replaceUrl) {
          window.history.replaceState(historyState, '', nextUrl)
        } else {
          window.history.pushState(historyState, '', nextUrl)
        }

        if (typeof setActiveSection === 'function') {
          setActiveSection('challenges', {
            preserveModuleContext: true,
            skipUrl: true,
          })
          return
        }

        window.location.assign(nextUrl)
      },
      [setActiveSection]
    )

  /* =======================================================
     CLIC DEPUIS UNE CARTE
     ======================================================= */

  const handleOpenTarget =
    useCallback(
      async (module, target) => {
        if (
          !isModuleAccessible(
            module
          )
        ) {
          setActionError(
            "Ce module n'est pas encore accessible."
          )

          return
        }

        const actionKey =
          `${getModuleSlug(module)}:${target}`

        setOpeningAction(
          actionKey
        )

        setActionError('')

        try {
          /*
           * La liste et l’API de détail utilisent le slug.
           */
          const moduleDetail =
            await fetchModuleDetail(
              getModuleSlug(module)
            )

          if (
            target ===
              MODULE_TARGETS.QUIZ &&
            moduleDetail
              .quiz_disponible ===
              false
          ) {
            throw new Error(
              labels.quizUnavailable
            )
          }

          if (
            target ===
            MODULE_TARGETS.CHALLENGE
          ) {
            saveModuleNavigation(
              moduleDetail,
              target
            )

            openChallengePage(
              moduleDetail
            )

            return
          }

          openModuleView(
            moduleDetail,
            target
          )
        } catch (requestError) {
          console.error(
            `Erreur pendant l'ouverture de ${target} :`,
            requestError
          )

          setActionError(
            getErrorMessage(
              requestError
            )
          )
        } finally {
          setOpeningAction('')
        }
      },
      [
        fetchModuleDetail,
        getErrorMessage,
        labels.quizUnavailable,
        openChallengePage,
        openModuleView,
        saveModuleNavigation,
      ]
    )

  const handleStartModule =
    useCallback(
      (module) => {
        handleOpenTarget(
          module,
          MODULE_TARGETS.READ
        )
      },
      [handleOpenTarget]
    )

  /* =======================================================
     RETOUR AU CATALOGUE
     ======================================================= */

  const handleBackToModules =
    useCallback(
      (replaceUrl = false) => {
        setSelectedModule(null)

        setActiveView(
          MODULE_VIEWS.CATALOG
        )

        setOpeningAction('')
        setActionError('')

        restoredModuleRef.current =
          ''

        const nextUrl = buildDashboardUrl({
          section: 'learning',
        })

        const moduleStorageKeys = [
          STORAGE_KEYS
            .SELECTED_MODULE,
          STORAGE_KEYS
            .CURRENT_MODULE,
          STORAGE_KEYS
            .MODULE_TARGET,
          STORAGE_KEYS
            .MODULE_NAVIGATION,
          STORAGE_KEYS
            .CHALLENGE_MODULE,
          STORAGE_KEYS
            .CHALLENGE_MODULE_ID,
          STORAGE_KEYS
            .CHALLENGE_MODULE_SLUG,
        ]

        moduleStorageKeys.forEach(
          (storageKey) => {
            try {
              sessionStorage.removeItem(
                storageKey
              )
            } catch (
              storageError
            ) {
              console.error(
                'Impossible de supprimer le contexte du module :',
                storageError
              )
            }
          }
        )

        if (replaceUrl) {
          window.history.replaceState(
            {
              section: 'learning',
            },
            '',
            nextUrl
          )
        } else {
          window.history.pushState(
            {
              section: 'learning',
            },
            '',
            nextUrl
          )
        }

        window.scrollTo({
          top: 0,
          behavior: 'smooth',
        })
      },
      []
    )

  /* =======================================================
     RESTAURATION DEPUIS LE SLUG
     ======================================================= */

  useEffect(() => {
    const handlePopState = () => {
      restoredModuleRef.current =
        ''

      setNavigationVersion(
        (currentVersion) =>
          currentVersion + 1
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
  }, [])

  useEffect(() => {
    if (
      isLoading ||
      error ||
      sortedModules.length === 0
    ) {
      return
    }

    const parsedLocation = parseDashboardLocation()

    /*
     * Si le dashboard affiche une autre section,
     * Learning ne restaure rien.
     */
    if (parsedLocation.section !== 'learning') {
      return
    }

    const moduleSlug = String(
      parsedLocation.moduleSlug || ''
    ).trim()

    if (!moduleSlug) {
      if (
        activeView !==
          MODULE_VIEWS.CATALOG ||
        selectedModule
      ) {
        setSelectedModule(null)

        setActiveView(
          MODULE_VIEWS.CATALOG
        )

        setOpeningAction('')
      }

      restoredModuleRef.current =
        ''

      return
    }

    const requestedTarget =
      parsedLocation.view === MODULE_TARGETS.QUIZ
        ? MODULE_TARGETS.QUIZ
        : MODULE_TARGETS.READ

    const restoreKey =
      `${moduleSlug}:${requestedTarget}`

    if (
      restoredModuleRef.current ===
      restoreKey
    ) {
      return
    }

    const matchingModule =
      sortedModules.find(
        (module) =>
          getModuleSlug(module) ===
          moduleSlug
      )

    if (!matchingModule) {
      setActionError(
        `Aucun module ne correspond au slug « ${moduleSlug} ».`
      )

      return
    }

    if (
      !isModuleAccessible(
        matchingModule
      )
    ) {
      setActionError(
        "Ce module n'est pas encore accessible."
      )

      return
    }

    restoredModuleRef.current =
      restoreKey

    setOpeningAction(
      `${getModuleSlug(matchingModule)}:${requestedTarget}`
    )

    let cancelled = false

    fetchModuleDetail(
      getModuleSlug(matchingModule)
    )
      .then((moduleDetail) => {
        if (cancelled) {
          return
        }

        let safeTarget =
          requestedTarget

        if (
          requestedTarget ===
            MODULE_TARGETS.QUIZ &&
          moduleDetail
            .quiz_disponible ===
            false
        ) {
          safeTarget =
            MODULE_TARGETS.READ
        }

        openModuleView(
          moduleDetail,
          safeTarget,
          true
        )
      })
      .catch((requestError) => {
        if (cancelled) {
          return
        }

        restoredModuleRef.current =
          ''

        setActionError(
          getErrorMessage(
            requestError
          )
        )
      })
      .finally(() => {
        if (!cancelled) {
          setOpeningAction('')
        }
      })

    return () => {
      cancelled = true
    }
  }, [
    activeView,
    error,
    fetchModuleDetail,
    getErrorMessage,
    isLoading,
    navigationVersion,
    openModuleView,
    sortedModules,
  ])

  /* =======================================================
     FAVORIS
     ======================================================= */

  const handleToggleBookmark =
    useCallback((moduleId) => {
      const normalizedId =
        String(moduleId)

      setBookmarkedModules(
        (currentBookmarks) => {
          const isBookmarked =
            currentBookmarks.includes(
              normalizedId
            )

          const nextBookmarks =
            isBookmarked
              ? currentBookmarks.filter(
                  (currentId) =>
                    currentId !==
                    normalizedId
                )
              : [
                  ...currentBookmarks,
                  normalizedId,
                ]

          try {
            localStorage.setItem(
              STORAGE_KEYS.BOOKMARKS,

              JSON.stringify(
                nextBookmarks
              )
            )
          } catch (storageError) {
            console.error(
              'Impossible d’enregistrer les favoris :',
              storageError
            )
          }

          return nextBookmarks
        }
      )
    }, [])

  /* =======================================================
     CHARGEMENT
     ======================================================= */

  if (isLoading) {
    return (
      <section
        className="dash-section learning-page"
        aria-busy="true"
        aria-live="polite"
      >
        <div className="learning-page__header">
          <div>
            <p className="learning-page__kicker">
              {labels.kicker}
            </p>

            <h1 className="learning-page__title">
              {labels.title}
            </h1>

            <p className="learning-page__subtitle">
              {labels.subtitle}
            </p>
          </div>
        </div>

        <div className="learning-page__grid">
          {Array.from(
            {
              length:
                modulesPerPage,
            },
            (_, index) =>
              index + 1
          ).map((item) => (
              <article
                className="learning-page__card learning-page__card--skeleton"
                key={item}
              >
                <div className="learning-page__cover learning-page__skeleton-cover" />

                <div className="learning-page__body">
                  <div className="learning-page__skeleton-line learning-page__skeleton-line--small" />

                  <div className="learning-page__skeleton-line learning-page__skeleton-line--title" />

                  <div className="learning-page__skeleton-line" />

                  <div className="learning-page__skeleton-line learning-page__skeleton-line--medium" />

                  <div className="learning-page__skeleton-steps">
                    <span />
                    <span />
                    <span />
                  </div>

                  <div className="learning-page__skeleton-line" />

                  <div className="learning-page__skeleton-actions">
                    <span />
                    <span />
                  </div>
                </div>
              </article>
            )
          )}
        </div>
      </section>
    )
  }

  /* =======================================================
     ERREUR DE CHARGEMENT
     ======================================================= */

  if (error) {
    return (
      <section className="dash-section learning-page">
        <div className="learning-page__header">
          <div>
            <p className="learning-page__kicker">
              {labels.kicker}
            </p>

            <h1 className="learning-page__title">
              {labels.title}
            </h1>

            <p className="learning-page__subtitle">
              {labels.subtitle}
            </p>
          </div>
        </div>

        <div className="learning-page__error">
          <span aria-hidden="true">
            ⚠️
          </span>

          <div>
            <h2>
              Une erreur est survenue
            </h2>

            <p>{error}</p>
          </div>

          <button
            type="button"
            onClick={loadModules}
          >
            {labels.retry}
          </button>
        </div>
      </section>
    )
  }

  /* =======================================================
     PAGE DE LECTURE
     ======================================================= */

  if (
    activeView ===
      MODULE_VIEWS.READ &&
    selectedModule
  ) {
    return (
      <Read
        module={selectedModule}
        getMediaUrl={getMediaUrl}
        onBack={() =>
          /*
           * Read.jsx modifie déjà l’URL avant
           * d’appeler ce callback.
           */
          handleBackToModules(true)
        }
        onOpenQuiz={() => {
          if (
            selectedModule
              .quiz_disponible ===
              false
          ) {
            setActionError(
              labels.quizUnavailable
            )

            return
          }

          /*
           * Read.jsx place déjà view=quiz
           * dans l’URL. On remplace donc
           * l’entrée au lieu d’en ajouter une.
           */
          openModuleView(
            selectedModule,
            MODULE_TARGETS.QUIZ,
            true
          )
        }}
        onOpenChallenge={() =>
          /*
           * Read.jsx place déjà section=challenges
           * dans l’URL.
           */
          openChallengePage(
            selectedModule,
            true
          )
        }
        onMarkedRead={async (progression) => {
          setSelectedModule((current) => ({
            ...current,
            est_lu: true,
            progression,
          }))

          await loadModules()
        }}
      />
    )
  }

  /* =======================================================
     PAGE QUIZ
     ======================================================= */

  if (
    activeView ===
      MODULE_VIEWS.QUIZ &&
    selectedModule
  ) {
    return (
      <Quiz
        module={selectedModule}
        onBack={() =>
          handleBackToModules()
        }
        onOpenLesson={() =>
          openModuleView(
            selectedModule,
            MODULE_TARGETS.READ
          )
        }
        onOpenChallenge={() =>
          openChallengePage(
            selectedModule
          )
        }
        onSubmit={async (quizResult) => {
          console.log('Résultat du quiz :', quizResult)

          try {
            const refreshedModule =
              await fetchModuleDetail(
                getModuleSlug(selectedModule)
              )

            setSelectedModule(refreshedModule)
            await loadModules()
          } catch (refreshError) {
            console.error(
              'Impossible de rafraîchir la progression après le quiz :',
              refreshError
            )
          }
        }}
      />
    )
  }



  return (
    <section className="dash-section learning-page">
      <div className="learning-page__header">
        <div>

          <h1 className="learning-page__title">
            {labels.title}
          </h1>

          <p className="learning-page__subtitle">
            {labels.subtitle}
          </p>
        </div>

        <span className="learning-page__count">
          {sortedModules.length}{' '}

          {sortedModules.length > 1
            ? labels.modules
            : labels.module.toLowerCase()}
        </span>
      </div>

      {actionError && (
        <div
          className="learning-page__action-message"
          role="alert"
        >
          <span aria-hidden="true">
            ⚠️
          </span>

          <p>{actionError}</p>

          <button
            type="button"
            onClick={() =>
              setActionError('')
            }
            aria-label="Fermer le message"
          >
            ×
          </button>
        </div>
      )}

      {sortedModules.length === 0 ? (
        <div className="learning-page__empty">
          {labels.empty}
        </div>
      ) : (
        <>
          <div
            ref={gridRef}
            className="learning-page__grid"
            onScroll={
              handleMobileGridScroll
            }
            onPointerDown={
              handleMobilePointerDown
            }
            onPointerMove={
              handleMobilePointerMove
            }
            onPointerUp={
              handleMobilePointerUp
            }
            onPointerCancel={
              handleMobilePointerCancel
            }
            onClickCapture={
              handleMobileGridClickCapture
            }
            onDragStart={(event) =>
              event.preventDefault()
            }
            style={
              modulesPerPage === 1
                ? {
                    width: '100%',
                    display: 'flex',
                    alignItems:
                      'stretch',
                    gap: '14px',
                    marginTop: '4px',
                    marginBottom:
                      '4px',
                    padding:
                      '2px 1px 5px',
                    overflowX:
                      'auto',
                    overflowY:
                      'hidden',
                    scrollSnapType:
                      'x mandatory',
                    scrollPaddingInline:
                      '1px',
                    scrollbarWidth:
                      'none',
                    overscrollBehaviorX:
                      'contain',
                    touchAction: 'pan-y',
                    cursor: 'grab',
                    userSelect: 'none',
                    WebkitOverflowScrolling:
                      'touch',
                  }
                : {
                    width: '100%',
                    display: 'grid',
                    gridTemplateColumns:
                      `repeat(${modulesPerPage}, minmax(0, 1fr))`,
                    alignItems:
                      'stretch',
                    gap: '24px',
                    marginTop: '8px',
                    marginBottom:
                      '12px',
                    overflow:
                      'visible',
                    scrollSnapType:
                      'none',
                  }
            }
          >
            {paginatedModules.map(
              (
                module,
                moduleIndex
              ) => {
                const status =
                  getModuleStatus(
                    module
                  )

                const imageUrl =
                  getMediaUrl(
                    module
                      ?.image_couverture
                  )

                const period =
                  formatModulePeriod(
                    module
                  )

                const globalModuleIndex =
                  modulesPerPage === 1
                    ? moduleIndex
                    : (
                        currentPage - 1
                      ) *
                        modulesPerPage +
                      moduleIndex

                const moduleOrder =
                  getModuleDisplayOrder(
                    module,
                    globalModuleIndex
                  )

                const accessible =
                  isModuleAccessible(
                    module
                  )

                const moduleSlug =
                  getModuleSlug(module)

                const readActionKey =
                  `${moduleSlug}:${MODULE_TARGETS.READ}`

                const quizActionKey =
                  `${moduleSlug}:${MODULE_TARGETS.QUIZ}`

                const challengeActionKey =
                  `${moduleSlug}:${MODULE_TARGETS.CHALLENGE}`

                const isOpeningRead =
                  openingAction ===
                  readActionKey

                const isOpeningQuiz =
                  openingAction ===
                  quizActionKey

                const isOpeningChallenge =
                  openingAction ===
                  challengeActionKey

                const isOpeningModule =
                  isOpeningRead ||
                  isOpeningQuiz ||
                  isOpeningChallenge

                const isBookmarked =
                  bookmarkedModules.includes(
                    String(module.id)
                  )

                const mainActionLabel =
                  module?.est_termine
                    ? labels.restart
                    : module?.est_lu
                      ? labels.continue
                      : labels.start

                const lessonsCount =
                  getLessonsCount(
                    module
                  )

                const questionsCount =
                  getQuestionsCount(
                    module
                  )

                const challengeCount =
                  getChallengeCount(
                    module
                  )

                return (
                  <article
                    key={
                      module.id ||
                      getModuleSlug(module)
                    }
                    className={[
                      'learning-page__card',

                      `learning-page__card--${status.key}`,

                      !accessible
                        ? 'learning-page__card--disabled'
                        : '',

                      isOpeningModule
                        ? 'learning-page__card--opening'
                        : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                  >
                    <div className="learning-page__cover">
                      <div className="learning-page__fallback">
                        <span aria-hidden="true">
                          💧
                        </span>
                      </div>

                      {imageUrl && (
                        <img
                          src={imageUrl}
                          alt={
                            module?.titre
                              ? `Illustration du module ${module.titre}`
                              : 'Illustration du module'
                          }
                          loading="lazy"
                          onError={(
                            event
                          ) => {
                            event.currentTarget.style.display =
                              'none'
                          }}
                        />
                      )}


                      <div className="learning-page__cover-badges">
                        <span className="learning-page__cover-level">
                          {module?.niveau ||
                            labels.beginner}
                        </span>

                        <span className="learning-page__cover-order">
                          {labels.module}{' '}
                          {moduleOrder}
                        </span>
                      </div>

                      <button
                        type="button"
                        className={[
                          'learning-page__bookmark',

                          isBookmarked
                            ? 'is-active'
                            : '',
                        ]
                          .filter(Boolean)
                          .join(' ')}
                        onClick={() =>
                          handleToggleBookmark(
                            module.id
                          )
                        }
                        aria-label={
                          isBookmarked
                            ? 'Retirer des favoris'
                            : 'Ajouter aux favoris'
                        }
                        aria-pressed={
                          isBookmarked
                        }
                      >
                        {isBookmarked
                          ? '★'
                          : '☆'}
                      </button>

                      <span
                        className={[
                          'learning-page__cover-status',

                          `learning-page__cover-status--${status.key}`,
                        ].join(' ')}
                      >
                        <span aria-hidden="true">
                          {status.icon}
                        </span>

                        {status.label}
                      </span>
                    </div>

                    <div className="learning-page__body">

                      <h2 className="learning-page__module-title">
                        {module?.titre ||
                          `${labels.module} ${moduleOrder}`}
                      </h2>

                      <p className="learning-page__summary">
                        {module?.resume ||
                          'Découvrez les notions essentielles de ce module et réalisez les activités proposées.'}
                      </p>

                      <div className="learning-page__steps">
                        <button
                          type="button"
                          className="learning-page__step learning-page__step--read"
                          disabled={
                            !accessible ||
                            isOpeningModule
                          }
                          onClick={() =>
                            handleOpenTarget(
                              module,
                              MODULE_TARGETS.READ
                            )
                          }
                          aria-label={`${labels.read} — ${lessonsCount} ${labels.lessons}`}
                        >
                          <span className="learning-page__step-icon">
                            📖
                          </span>

                          <span className="learning-page__step-content">
                            <strong>
                              {isOpeningRead
                                ? '…'
                                : lessonsCount}
                            </strong>

                            <small>
                              {labels.lessons}
                            </small>
                          </span>
                        </button>

                        <button
                          type="button"
                          className="learning-page__step learning-page__step--quiz"
                          disabled={
                            !accessible ||
                            isOpeningModule
                          }
                          onClick={() =>
                            handleOpenTarget(
                              module,
                              MODULE_TARGETS.QUIZ
                            )
                          }
                          aria-label={`${labels.quiz} — ${questionsCount} ${labels.questions}`}
                        >
                          <span className="learning-page__step-icon">
                            ❓
                          </span>

                          <span className="learning-page__step-content">
                            <strong>
                              {isOpeningQuiz
                                ? '…'
                                : questionsCount}
                            </strong>

                            <small>
                              {labels.questions}
                            </small>
                          </span>
                        </button>

                        <button
                          type="button"
                          className="learning-page__step learning-page__step--challenge"
                          disabled={
                            !accessible ||
                            isOpeningModule
                          }
                          onClick={() =>
                            handleOpenTarget(
                              module,
                              MODULE_TARGETS.CHALLENGE
                            )
                          }
                          aria-label={`${labels.challenge} — ${challengeCount} ${labels.challenges}`}
                        >
                          <span className="learning-page__step-icon">
                            🏆
                          </span>

                          <span className="learning-page__step-content">
                            <strong>
                              {isOpeningChallenge
                                ? '…'
                                : challengeCount}
                            </strong>

                            <small>
                              {labels.challenges}
                            </small>
                          </span>
                        </button>
                      </div>

                      {period && (
                        <p className="learning-page__period">
                          <span aria-hidden="true">
                            📅
                          </span>

                          {period}
                        </p>
                      )}

                      {module?.points !==
                        undefined &&
                        module?.points !==
                          null && (
                          <p className="learning-page__points">
                            <span aria-hidden="true">
                              ⭐
                            </span>

                            {Number(
                              module.points
                            )}{' '}
                            points
                          </p>
                        )}

                      <div className="learning-page__progress">
                        <div className="learning-page__progress-track">
                          <div
                            className="learning-page__progress-fill"
                            style={{
                              width:
                                `${status.progress}%`,
                            }}
                          />
                        </div>

                        <strong>
                          {status.progress}%
                        </strong>
                      </div>

                      <div className="learning-page__actions">
                        <button
                          type="button"
                          className="learning-page__start"
                          disabled={
                            !accessible ||
                            isOpeningModule
                          }
                          onClick={() =>
                            handleStartModule(
                              module
                            )
                          }
                        >
                          <span aria-hidden="true">
                            {accessible
                              ? '▶'
                              : '🔒'}
                          </span>

                          <span>
                            {isOpeningRead
                              ? labels.opening
                              : accessible
                                ? mainActionLabel
                                : labels.locked}
                          </span>
                        </button>

                        <button
                          type="button"
                          className="learning-page__details"
                          disabled={
                            !accessible ||
                            isOpeningModule
                          }
                          onClick={() =>
                            handleOpenTarget(
                              module,
                              MODULE_TARGETS.READ
                            )
                          }
                        >
                          <span>
                            {labels.details}
                          </span>

                          <span aria-hidden="true">
                            →
                          </span>
                        </button>
                      </div>
                    </div>
                  </article>
                )
              }
            )}
          </div>

          {totalPages > 1 && (
            <nav
              className="learning-page__pagination"
              aria-label="Pagination des modules"
            >
              <button
                type="button"
                className="learning-page__pagination-control"
                disabled={
                  currentPage === 1
                }
                onClick={() =>
                  handlePageChange(
                    currentPage - 1
                  )
                }
                aria-label="Afficher la page précédente"
              >
                <span aria-hidden="true">
                  ←
                </span>

                <span className="learning-page__pagination-control-label">
                  Précédent
                </span>
              </button>

              <div className="learning-page__pagination-pages">
                {Array.from(
                  {
                    length:
                      totalPages,
                  },
                  (_, index) =>
                    index + 1
                ).map((page) => (
                  <button
                    key={page}
                    type="button"
                    className={[
                      'learning-page__pagination-number',

                      page ===
                      currentPage
                        ? 'is-active'
                        : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    aria-current={
                      page ===
                      currentPage
                        ? 'page'
                        : undefined
                    }
                    aria-label={`Afficher la page ${page}`}
                    onClick={() =>
                      handlePageChange(
                        page
                      )
                    }
                  >
                    {page}
                  </button>
                ))}
              </div>

              <button
                type="button"
                className="learning-page__pagination-control"
                disabled={
                  currentPage ===
                  totalPages
                }
                onClick={() =>
                  handlePageChange(
                    currentPage + 1
                  )
                }
                aria-label="Afficher la page suivante"
              >
                <span className="learning-page__pagination-control-label">
                  Suivant
                </span>

                <span aria-hidden="true">
                  →
                </span>
              </button>
            </nav>
          )}
        </>
      )}
    </section>
  )
}

export default LearningSection