import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'

import { createPortal } from 'react-dom'
import {
  AnimatePresence,
  motion,
} from 'framer-motion'

import './Dashboard.css'

import DashboardHome from './dashboardSections/DashboardHome'
import LearningSection from './dashboardSections/LearningSection'
import ChallengesSection from './dashboardSections/ChallengesSection'
import SubmitActivitySection from './dashboardSections/SubmitActivitySection'
import MyActivitiesSection from './dashboardSections/MyActivitiesSection'
import CommunityProjectsSection from './dashboardSections/CommunityProjectsSection'
import CommunitySection from './dashboardSections/CommunitySection'
import BadgesCertificatesSection from './dashboardSections/BadgesCertificatesSection'
import ProfileSection from './dashboardSections/ProfileSection'
import HelpSection from './dashboardSections/HelpSection'

import { getDashboardData } from './dashboardSections/dashboardData'
import { getApiErrorMessage } from '../api/api'
import { notificationsApi } from '../api/services'
import {
  buildDashboardUrl,
  parseDashboardLocation,
} from '../utils/dashboardRoutes'


const DASHBOARD_SECTIONS = [
  'dashboard',
  'learning',
  'challenges',
  'submit',
  'activities',
  'projects',
  'community',
  'badges',
  'profile',
  'aide',
  'deconnexion'
]


const getSectionFromLocation = () => {
  const parsedLocation = parseDashboardLocation()

  return DASHBOARD_SECTIONS.includes(parsedLocation.section)
    ? parsedLocation.section
    : 'dashboard'
}

function Dashboard({
  user,
  onLogout,
  onUserUpdate,
}) {
  const [language, setLanguage] =
    useState('FR')

  /*
   * La première section est directement récupérée
   * depuis l’URL.
   */
  const [
    activeSection,
    setActiveSection,
  ] = useState(() =>
    getSectionFromLocation()
  )

  const [
    showNotifications,
    setShowNotifications,
  ] = useState(false)

  const [notifications, setNotifications] = useState([])
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(false)
  const [notificationsError, setNotificationsError] = useState('')

  const [
    showMobileMenu,
    setShowMobileMenu,
  ] = useState(false)

  const [
    showLogoutConfirm,
    setShowLogoutConfirm,
  ] = useState(false)

  const [
    activities,
    setActivities,
  ] = useState(() => {
    try {
      const savedActivities =
        localStorage.getItem(
          'waterChallengeActivities'
        )

      return savedActivities
        ? JSON.parse(savedActivities)
        : []
    } catch (error) {
      console.error(
        'Impossible de récupérer les activités :',
        error
      )

      return []
    }
  })

  const [
    projects,
    setProjects,
  ] = useState(() => {
    try {
      const savedProjects =
        localStorage.getItem(
          'waterChallengeProjects'
        )

      return savedProjects
        ? JSON.parse(savedProjects)
        : []
    } catch (error) {
      console.error(
        'Impossible de récupérer les projets :',
        error
      )

      return []
    }
  })

  const data = useMemo(
    () => getDashboardData(language),
    [language]
  )

  const t = data.text

  /*
   * Compatibilité avec les données
   * retournées par le backend.
   */
  const currentUser = useMemo(() => {
    const profile =
      user?.profile || {}

    const fullNameParts =
      user?.full_name
        ? user.full_name
            .trim()
            .split(/\s+/)
        : []

    const fallbackFirstName =
      fullNameParts.length > 0
        ? fullNameParts[0]
        : 'Water'

    const fallbackLastName =
      fullNameParts.length > 1
        ? fullNameParts
            .slice(1)
            .join(' ')
        : 'Ambassador'

    return {
      id:
        user?.id ?? null,

      prenom:
        user?.first_name ||
        user?.prenom ||
        fallbackFirstName,

      nom:
        user?.last_name ||
        user?.nom ||
        fallbackLastName,

      email:
        user?.email ||
        'ambassador@waterchallenge.mg',

      telephone:
        user?.phone ||
        user?.telephone ||
        'Non renseigné',

      birthDate:
        user?.birth_date ||
        user?.birthDate ||
        null,

      role:
        user?.role ||
        'ambassador',

      faritra:
        profile?.faritra ||
        profile?.region ||
        user?.faritra ||
        'Madagascar',

      fivondronana:
        profile?.fivondronana ||
        profile?.community ||
        user?.fivondronana ||
        'Communauté locale',

      scoutType:
        profile?.scout_type ||
        profile?.scoutType ||
        user?.scoutType ||
        'Guide et Scout',

      section:
        profile?.section ||
        user?.section ||
        'Mavo',

      position:
        profile?.position ||
        user?.position ||
        'Beazina',

      niveau:
        profile?.niveau ||
        profile?.level ||
        user?.niveau ||
        t.levelBeginner,

      badge:
        profile?.badge ||
        user?.badge ||
        t.firstBadge,

      points:
        profile?.points ??
        user?.points ??
        120,

      progression:
        profile?.progression ??
        profile?.progress ??
        user?.progression ??
        38,

      isActive:
        user?.is_active ??
        true,

      isEmailVerified:
        user?.is_email_verified ??
        false,

      createdAt:
        user?.created_at ||
        null,
    }
  }, [user, t])

  const userInitials = useMemo(() => {
    const firstInitial =
      currentUser.prenom
        ?.charAt(0)
        ?.toUpperCase() || 'W'

    const lastInitial =
      currentUser.nom
        ?.charAt(0)
        ?.toUpperCase() || 'A'

    return `${firstInitial}${lastInitial}`
  }, [
    currentUser.prenom,
    currentUser.nom,
  ])

  const loadNotifications = useCallback(async () => {
    setIsLoadingNotifications(true)
    setNotificationsError('')

    try {
      const receivedNotifications = await notificationsApi.list()
      setNotifications(receivedNotifications)
    } catch (requestError) {
      console.error('Impossible de charger les notifications :', requestError)
      setNotificationsError(
        getApiErrorMessage(
          requestError,
          'Impossible de charger les notifications.'
        )
      )
    } finally {
      setIsLoadingNotifications(false)
    }
  }, [])

  useEffect(() => {
    loadNotifications()

    const refresh = () => loadNotifications()
    const refreshWhenVisible = () => {
      if (document.visibilityState === 'visible') {
        loadNotifications()
      }
    }
    const pollingId = window.setInterval(loadNotifications, 60_000)

    window.addEventListener('waterchallenge:data-updated', refresh)
    document.addEventListener('visibilitychange', refreshWhenVisible)

    return () => {
      window.clearInterval(pollingId)
      window.removeEventListener('waterchallenge:data-updated', refresh)
      document.removeEventListener('visibilitychange', refreshWhenVisible)
    }
  }, [loadNotifications])

  useEffect(() => {
    if (showNotifications) {
      loadNotifications()
    }
  }, [loadNotifications, showNotifications])

  const notificationItems = useMemo(
    () => (Array.isArray(notifications) ? notifications : []),
    [notifications]
  )

  const unreadNotificationsCount = useMemo(
    () => notificationItems.filter((notification) => !notification.est_lue).length,
    [notificationItems]
  )

  const markNotificationAsRead = useCallback(async (notification) => {
    if (!notification?.id || notification.est_lue) {
      return notification
    }

    try {
      const updated = await notificationsApi.markRead(notification.id)
      setNotifications((current) =>
        current.map((item) =>
          String(item.id) === String(notification.id)
            ? { ...item, ...updated, est_lue: true }
            : item
        )
      )
      return updated
    } catch (requestError) {
      setNotificationsError(
        getApiErrorMessage(
          requestError,
          'Impossible de marquer cette notification comme lue.'
        )
      )
      return notification
    }
  }, [])

  const markAllNotificationsAsRead = useCallback(async () => {
    try {
      await notificationsApi.markAllRead()
      setNotifications((current) =>
        current.map((notification) => ({
          ...notification,
          est_lue: true,
          lue_le: notification.lue_le || new Date().toISOString(),
        }))
      )
    } catch (requestError) {
      setNotificationsError(
        getApiErrorMessage(
          requestError,
          'Impossible de marquer toutes les notifications comme lues.'
        )
      )
    }
  }, [])

  const openNotification = useCallback(
    async (notification) => {
      await markNotificationAsRead(notification)

      const challengeMatch = String(notification?.lien || '').match(
        /\/challenges\/defis\/([^/]+)\/?/
      )

      if (challengeMatch) {
        const challengeId = challengeMatch[1]

        window.history.pushState(
          { section: 'challenges', challengeId },
          '',
          buildDashboardUrl({
            section: 'challenges',
            challengeId,
          })
        )
        setActiveSection('challenges')
      }

      setShowNotifications(false)
    },
    [markNotificationAsRead]
  )

  const menuItems = [
    {
      id: 'dashboard',
      icon: '🏠',
      label: t.menu.dashboard,
    },
    {
      id: 'learning',
      icon: '📚',
      label: t.menu.learning,
    },
    {
      id: 'challenges',
      icon: '🏆',
      label: t.menu.challenges,
    },
    {
      id: 'submit',
      icon: '📤',
      label: t.menu.submit,
    },
    {
      id: 'activities',
      icon: '📁',
      label: t.menu.activities,
    },
    {
      id: 'projects',
      icon: '🌍',
      label: t.menu.projects,
    },
    {
      id: 'community',
      icon: '👥',
      label: t.menu.community,
    },
    {
      id: 'badges',
      icon: '🏅',
      label: t.menu.badges,
    },
    {
      id: 'profile',
      icon: '👤',
      label: t.menu.profile,
    },
    {
      id: 'aide',
      icon: '❓',
      label:
        language === 'FR'
          ? 'Aide'
          : 'Fanampiana',
    },
    {
      id: 'deconnexion',
      icon: '↪',
      label: t.logout,
    },
  ]

  const clearStoredModuleContext = () => {
    const storageKeys = [
      'waterChallengeSelectedModule',
      'waterChallengeCurrentModule',
      'waterChallengeModuleTarget',
      'waterChallengeModuleNavigation',
      'waterChallengeChallengeModule',
      'waterChallengeChallengeModuleId',
      'waterChallengeChallengeModuleSlug',
    ]

    storageKeys.forEach((storageKey) => {
      try {
        sessionStorage.removeItem(storageKey)
      } catch (storageError) {
        console.error(
          'Impossible de nettoyer le contexte du module :',
          storageError
        )
      }
    })
  }

  /*
   * Navigation interne du Dashboard.
   * Les sections générales gardent les anciennes URL en hash.
   * Les vues d'un module utilisent leur route avec slug et passent
   * skipUrl=true après avoir déjà construit cette route.
   */
  const handleSectionChange = (
    sectionId,
    options = {}
  ) => {
    if (!DASHBOARD_SECTIONS.includes(sectionId)) {
      console.error(
        `Section Dashboard inconnue : ${sectionId}`
      )
      return
    }

    const {
      preserveModuleContext = false,
      skipUrl = false,
      replace = false,
    } = options

    if (!preserveModuleContext) {
      clearStoredModuleContext()
    }

    setActiveSection(sectionId)
    setShowMobileMenu(false)
    setShowNotifications(false)

    if (!skipUrl) {
      const nextUrl = buildDashboardUrl({ section: sectionId })
      const historyState = { section: sectionId }

      if (replace) {
        window.history.replaceState(historyState, '', nextUrl)
      } else {
        window.history.pushState(historyState, '', nextUrl)
      }

      window.dispatchEvent(
        new PopStateEvent('popstate', {
          state: historyState,
        })
      )
    }

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  const saveActivities = (
    nextActivities
  ) => {
    setActivities(nextActivities)

    localStorage.setItem(
      'waterChallengeActivities',
      JSON.stringify(
        nextActivities
      )
    )
  }

  const saveProjects = (
    nextProjects
  ) => {
    setProjects(nextProjects)

    localStorage.setItem(
      'waterChallengeProjects',
      JSON.stringify(
        nextProjects
      )
    )
  }

  const handleAddActivity = (
    activity
  ) => {
    const nextActivity = {
      id:
        typeof crypto !==
          'undefined' &&
        crypto.randomUUID
          ? crypto.randomUUID()
          : Date.now(),

      ...activity,

      status: 'pending',

      createdAt:
        new Date().toISOString(),

      author:
        `${currentUser.prenom} ${currentUser.nom}`.trim(),
    }

    const nextActivities = [
      nextActivity,
      ...activities,
    ]

    saveActivities(
      nextActivities
    )


    handleSectionChange(
      'activities'
    )
  }

  const handleAddProject = (
    project
  ) => {
    const nextProject = {
      id:
        typeof crypto !==
          'undefined' &&
        crypto.randomUUID
          ? crypto.randomUUID()
          : Date.now(),

      ...project,

      progress:
        Number(
          project.progress || 0
        ),

      photos:
        project.photos || '',

      createdAt:
        new Date().toISOString(),

      author:
        `${currentUser.prenom} ${currentUser.nom}`.trim(),
    }

    const nextProjects = [
      nextProject,
      ...projects,
    ]

    saveProjects(nextProjects)
  }

  const handleLogoutClick = () => {
    setShowMobileMenu(false)
    setShowNotifications(false)

    onLogout()
  }

  /*
   * Ouvre la fenêtre de confirmation avant
   * toute déconnexion effective.
   */
  const requestLogout = () => {
    setShowMobileMenu(false)
    setShowNotifications(false)
    setShowLogoutConfirm(true)
  }

  const confirmLogout = () => {
    setShowLogoutConfirm(false)
    handleLogoutClick()
  }

  const cancelLogout = () => {
    setShowLogoutConfirm(false)
  }

  const handleMenuItemClick = (
    itemId
  ) => {
    if (itemId === 'deconnexion') {
      requestLogout()

      return
    }

    handleSectionChange(itemId)
  }

  useEffect(() => {
    const synchronizeSectionWithLocation = () => {
      const sectionFromLocation = getSectionFromLocation()

      setActiveSection(sectionFromLocation)
      setShowMobileMenu(false)
      setShowNotifications(false)

      window.scrollTo({
        top: 0,
        behavior: 'auto',
      })
    }

    synchronizeSectionWithLocation()

    window.addEventListener(
      'popstate',
      synchronizeSectionWithLocation
    )
    window.addEventListener(
      'hashchange',
      synchronizeSectionWithLocation
    )

    return () => {
      window.removeEventListener(
        'popstate',
        synchronizeSectionWithLocation
      )
      window.removeEventListener(
        'hashchange',
        synchronizeSectionWithLocation
      )
    }
  }, [])

  useEffect(() => {
    const handleResize = () => {
      if (
        window.innerWidth > 1050
      ) {
        setShowMobileMenu(false)
      }
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
    if (!showMobileMenu) {
      document.body.style.overflow =
        ''

      return undefined
    }

    document.body.style.overflow =
      'hidden'

    return () => {
      document.body.style.overflow =
        ''
    }
  }, [showMobileMenu])

  /*
   * Fermeture avec la touche Échap.
   */
  useEffect(() => {
    const handleEscape = (
      event
    ) => {
      if (
        event.key !== 'Escape'
      ) {
        return
      }

      setShowMobileMenu(false)
      setShowNotifications(false)
      setShowLogoutConfirm(false)
    }

    window.addEventListener(
      'keydown',
      handleEscape
    )

    return () => {
      window.removeEventListener(
        'keydown',
        handleEscape
      )
    }
  }, [])

  const handleProfileUpdate = (updatedUser) => {
    if (typeof onUserUpdate === 'function') {
      onUserUpdate(updatedUser)
    }
  }

  const renderSection = () => {
    const sharedProps = {
      t,
      data,
      language,
      user: currentUser,
      activities,
      projects,
      onProfileUpdate: handleProfileUpdate,

      setActiveSection:
        handleSectionChange,
    }

    switch (activeSection) {
      case 'learning':
        return (
          <LearningSection
            {...sharedProps}
          />
        )

      case 'challenges':
        return (
          <ChallengesSection
            {...sharedProps}
          />
        )

      case 'submit':
        return (
          <SubmitActivitySection
            {...sharedProps}
            onAddActivity={
              handleAddActivity
            }
          />
        )

      case 'activities':
        return (
          <MyActivitiesSection
            {...sharedProps}
          />
        )

      case 'projects':
        return (
          <CommunityProjectsSection
            {...sharedProps}
            onAddProject={
              handleAddProject
            }
          />
        )

      case 'community':
        return (
          <CommunitySection
            {...sharedProps}
          />
        )

      case 'badges':
        return (
          <BadgesCertificatesSection
            {...sharedProps}
          />
        )

      case 'profile':
        return (
          <ProfileSection
            {...sharedProps}
          />
        )

      case 'aide':
        return (
          <HelpSection
            {...sharedProps}
          />
        )

      case 'dashboard':
      default:
        return (
          <DashboardHome
            {...sharedProps}
          />
        )
    }
  }

  const notificationPortal =
    showNotifications &&
    typeof document !==
      'undefined'
      ? createPortal(
          <AnimatePresence>
            <motion.div
              className="dash-notification-overlay"
              initial={{
                opacity: 0,
              }}
              animate={{
                opacity: 1,
              }}
              exit={{
                opacity: 0,
              }}
              onClick={() =>
                setShowNotifications(
                  false
                )
              }
            >
              <motion.aside
                className="dash-notification-portal"
                role="dialog"
                aria-modal="true"
                aria-label={
                  t.home
                    .notificationsTitle
                }
                initial={{
                  opacity: 0,
                  y: -20,
                  scale: 0.96,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                  scale: 1,
                }}
                exit={{
                  opacity: 0,
                  y: -12,
                  scale: 0.96,
                }}
                transition={{
                  duration: 0.24,
                  ease: 'easeOut',
                }}
                onClick={(
                  event
                ) =>
                  event.stopPropagation()
                }
              >
                <div className="dash-notification-portal-head">
                  <div>
                    <span
                      aria-hidden="true"
                    >
                      🔔
                    </span>

                    <h3>
                      {
                        t.home
                          .notificationsTitle
                      }
                    </h3>
                  </div>

                  <div className="dash-notification-head-actions">
                    {unreadNotificationsCount > 0 && (
                      <button
                        type="button"
                        className="dash-notification-read-all"
                        onClick={markAllNotificationsAsRead}
                      >
                        Tout lire
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={() => setShowNotifications(false)}
                      aria-label="Fermer les notifications"
                    >
                      ×
                    </button>
                  </div>
                </div>

                <div className="dash-notification-portal-list">
                  {notificationsError && (
                    <div className="dash-notification-error">
                      <p>{notificationsError}</p>
                      <button type="button" onClick={loadNotifications}>
                        Réessayer
                      </button>
                    </div>
                  )}

                  {isLoadingNotifications && notificationItems.length === 0 ? (
                    <div className="dash-empty">Chargement des notifications…</div>
                  ) : notificationItems.length > 0 ? (
                    notificationItems.map((notification) => (
                      <button
                        type="button"
                        className={`dash-notification-row ${
                          notification.est_lue ? 'is-read' : 'is-unread'
                        }`}
                        key={notification.id}
                        onClick={() => openNotification(notification)}
                      >
                        <strong aria-hidden="true">
                          {notification.est_lue ? '✓' : '•'}
                        </strong>

                        <div>
                          <h4>{notification.titre || 'Notification'}</h4>
                          <p>{notification.message}</p>
                          {notification.cree_le && (
                            <small>
                              {new Date(notification.cree_le).toLocaleString('fr-FR')}
                            </small>
                          )}
                        </div>
                      </button>
                    ))
                  ) : (
                    <div className="dash-empty">
                      {language === 'FR'
                        ? 'Aucune notification pour le moment.'
                        : 'Tsy misy fampahafantarana amin’izao fotoana izao.'}
                    </div>
                  )}
                </div>

              </motion.aside>
            </motion.div>
          </AnimatePresence>,
          document.body
        )
      : null

  const logoutConfirmPortal =
    showLogoutConfirm &&
    typeof document !==
      'undefined'
      ? createPortal(
          <AnimatePresence>
            <motion.div
              className="dash-confirm-overlay"
              initial={{
                opacity: 0,
              }}
              animate={{
                opacity: 1,
              }}
              exit={{
                opacity: 0,
              }}
              onClick={cancelLogout}
            >
              <motion.div
                className="dash-confirm-modal"
                role="dialog"
                aria-modal="true"
                aria-label={
                  language === 'FR'
                    ? 'Confirmer la déconnexion'
                    : 'Hamarino ny fialàna'
                }
                initial={{
                  opacity: 0,
                  y: -14,
                  scale: 0.96,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                  scale: 1,
                }}
                exit={{
                  opacity: 0,
                  y: -10,
                  scale: 0.96,
                }}
                transition={{
                  duration: 0.22,
                  ease: 'easeOut',
                }}
                onClick={(
                  event
                ) =>
                  event.stopPropagation()
                }
              >
                <div className="dash-confirm-icon">
                  ↪
                </div>

                <h3>
                  {language === 'FR'
                    ? 'Se déconnecter ?'
                    : 'Hivoaka ?'}
                </h3>

                <p>
                  {language === 'FR'
                    ? 'Voulez-vous vraiment vous déconnecter de votre compte Water Challenge ?'
                    : 'Tena te hivoaka amin’ny kaontinao Water Challenge ve ianao ?'}
                </p>

                <div className="dash-confirm-actions">
                  <button
                    type="button"
                    className="dash-light-btn"
                    onClick={
                      cancelLogout
                    }
                  >
                    {language ===
                    'FR'
                      ? 'Annuler'
                      : 'Aoka'}
                  </button>

                  <button
                    type="button"
                    className="dash-confirm-danger-btn"
                    onClick={
                      confirmLogout
                    }
                  >
                    {language ===
                    'FR'
                      ? 'Se déconnecter'
                      : 'Mivoaka'}
                  </button>
                </div>
              </motion.div>
            </motion.div>
          </AnimatePresence>,
          document.body
        )
      : null

  return (
    <div className="dash-page">


      <motion.header
        className="dash-navbar dash-navbar-clean"
        initial={{
          opacity: 0,
          y: -22,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          duration: 0.55,
          ease: 'easeOut',
        }}
      >
        <div className="dash-navbar-left">
          <button
            type="button"
            className="dash-menu-toggle"
            onClick={() =>
              setShowMobileMenu(true)
            }
            aria-label="Ouvrir le menu"
            aria-expanded={
              showMobileMenu
            }
            aria-controls="dashboard-sidebar"
          >
            <span />
            <span />
            <span />
          </button>

          <button
            type="button"
            className="dash-logo"
            onClick={() =>
              handleSectionChange(
                'dashboard'
              )
            }
          >
            <span className="dash-logo-mark">
              W
            </span>

            <span>
              Water Challenge
            </span>
          </button>
        </div>

        <div className="dash-navbar-right">
          <button
            type="button"
            className="dash-notification-btn"
            onClick={() =>
              setShowNotifications(
                true
              )
            }
            title="Notifications"
            aria-label={`Notifications non lues : ${unreadNotificationsCount}`}
          >
            <span
              className="dash-notification-icon"
              aria-hidden="true"
            >
              🔔
            </span>

            {unreadNotificationsCount > 0 && (
              <span className="dash-notification-badge">
                {unreadNotificationsCount}
              </span>
            )}
          </button>

          <button
            type="button"
            className={`dash-navbar-quicklink ${
              activeSection ===
              'learning'
                ? 'active'
                : ''
            }`}
            onClick={() =>
              handleSectionChange(
                'learning'
              )
            }
            title={t.menu.learning}
            aria-label={
              t.menu.learning
            }
            aria-current={
              activeSection ===
              'learning'
                ? 'page'
                : undefined
            }
          >
            <span aria-hidden="true">
              📚
            </span>
          </button>

          <button
            type="button"
            className={`dash-navbar-quicklink ${
              activeSection ===
              'challenges'
                ? 'active'
                : ''
            }`}
            onClick={() =>
              handleSectionChange(
                'challenges'
              )
            }
            title={t.menu.challenges}
            aria-label={
              t.menu.challenges
            }
            aria-current={
              activeSection ===
              'challenges'
                ? 'page'
                : undefined
            }
          >
            <span aria-hidden="true">
              🏆
            </span>
          </button>

          <div className="dash-language">
            <button
              type="button"
              className={
                language === 'FR'
                  ? 'active'
                  : ''
              }
              onClick={() =>
                setLanguage('FR')
              }
              aria-pressed={
                language === 'FR'
              }
            >
              FR
            </button>

            <button
              type="button"
              className={
                language === 'MLG'
                  ? 'active'
                  : ''
              }
              onClick={() =>
                setLanguage('MLG')
              }
              aria-pressed={
                language === 'MLG'
              }
            >
              MLG
            </button>
          </div>

          <button
            type="button"
            className="dash-mini-user"
            onClick={() =>
              handleSectionChange(
                'profile'
              )
            }
            aria-label="Afficher le profil"
          >
            <span>
              {userInitials}
            </span>

            <div>
              <strong>
                {
                  currentUser.prenom
                }
              </strong>

              <small>
                {
                  currentUser.niveau
                }
              </small>
            </div>
          </button>

          <button
            type="button"
            className="dash-logout"
            onClick={
              requestLogout
            }
          >
            {t.logout}
          </button>
        </div>
      </motion.header>

      <div className="dash-shell dash-shell-wide">
        <AnimatePresence>
          {showMobileMenu && (
            <motion.button
              type="button"
              className="dash-sidebar-overlay"
              aria-label="Fermer le menu"
              onClick={() =>
                setShowMobileMenu(
                  false
                )
              }
              initial={{
                opacity: 0,
              }}
              animate={{
                opacity: 1,
              }}
              exit={{
                opacity: 0,
              }}
              transition={{
                duration: 0.25,
              }}
            />
          )}
        </AnimatePresence>

        <aside
          id="dashboard-sidebar"
          className={`dash-sidebar ${
            showMobileMenu
              ? 'is-open'
              : ''
          }`}
          aria-hidden={
            typeof window !==
              'undefined' &&
            window.innerWidth <=
              1050
              ? !showMobileMenu
              : false
          }
        >
          <div className="dash-mobile-menu-head">
            <button
              type="button"
              className="dash-logo"
              onClick={() =>
                handleSectionChange(
                  'dashboard'
                )
              }
            >
              <span className="dash-logo-mark">
                W
              </span>

              <span>
                Water Challenge
              </span>
            </button>

            <button
              type="button"
              className="dash-mobile-menu-close"
              onClick={() =>
                setShowMobileMenu(
                  false
                )
              }
              aria-label="Fermer le menu"
            >
              ×
            </button>
          </div>

         

          <nav
            className="dash-menu"
            aria-label="Navigation du Dashboard"
          >
            {menuItems.map(
              (item) => (
                <button
                  key={item.id}
                  type="button"
                  className={
                    activeSection ===
                    item.id
                      ? 'active'
                      : ''
                  }
                  onClick={() =>
                    handleMenuItemClick(
                      item.id
                    )
                  }
                  aria-current={
                    activeSection ===
                    item.id
                      ? 'page'
                      : undefined
                  }
                >
                  <span
                    aria-hidden="true"
                  >
                    {item.icon}
                  </span>

                  {item.label}
                </button>
              )
            )}
          </nav>

          <button
            type="button"
            className="dash-mobile-logout"
            onClick={
              requestLogout
            }
          >
            <span
              aria-hidden="true"
            >
              ↪
            </span>

            {t.logout}
          </button>
        </aside>

        <main className="dash-content">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeSection}
              initial={{
                opacity: 0,
                y: 18,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              exit={{
                opacity: 0,
                y: -12,
              }}
              transition={{
                duration: 0.32,
                ease: 'easeOut',
              }}
            >
              {renderSection()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {notificationPortal}
      {logoutConfirmPortal}
    </div>
  )
}

export default Dashboard
