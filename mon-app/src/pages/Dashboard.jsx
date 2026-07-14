import {
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
import { label } from 'framer-motion/client'

/*
 * Liste des sections autorisées dans le hash.
 *
 * Exemples :
 * #dashboard
 * #learning
 * #challenges
 * #submit
 */
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


const getRawHashSection = () => {
  if (typeof window === 'undefined') {
    return ''
  }

  try {
    return decodeURIComponent(
      window.location.hash
        .replace(/^#\/?/, '')
        .trim()
        .toLowerCase()
    )
  } catch (error) {
    console.error(
      'Impossible de décoder le hash :',
      error
    )

    return ''
  }
}


const getSectionFromHash = () => {
  const hashSection =
    getRawHashSection()

  return DASHBOARD_SECTIONS.includes(
    hashSection
  )
    ? hashSection
    : 'dashboard'
}

function Dashboard({
  user,
  onLogout,
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
    getSectionFromHash()
  )

  const [
    showNotifications,
    setShowNotifications,
  ] = useState(false)

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

  const pendingCount = useMemo(() => {
    return activities.filter(
      (activity) =>
        activity.status === 'pending'
    ).length
  }, [activities])

  const notificationItems =
    useMemo(() => {
      const baseNotifications =
        Array.isArray(
          data.notifications
        )
          ? data.notifications
          : []

      if (pendingCount <= 0) {
        return baseNotifications
      }

      const pendingNotification =
        language === 'FR'
          ? `${pendingCount} activité(s) en attente de validation.`
          : `${pendingCount} asa miandry fanamarinana.`

      return [
        ...baseNotifications,
        pendingNotification,
      ]
    }, [
      data.notifications,
      pendingCount,
      language,
    ])

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

  /*
   * Navigation interne du Dashboard.
   *
   * Chaque section est également enregistrée
   * dans le hash de l’URL.
   */
  const handleSectionChange = (
    sectionId
  ) => {
    if (
      !DASHBOARD_SECTIONS.includes(
        sectionId
      )
    ) {
      console.error(
        `Section Dashboard inconnue : ${sectionId}`
      )

      return
    }

    setActiveSection(sectionId)
    setShowMobileMenu(false)
    setShowNotifications(false)

    const nextHash =
      `#${sectionId}`

    /*
     * Modifier location.hash ajoute une entrée
     * dans l’historique du navigateur.
     */
    if (
      window.location.hash !==
      nextHash
    ) {
      window.location.hash =
        sectionId
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
    const synchronizeSectionWithHash =
      () => {
        const sectionFromHash =
          getSectionFromHash()

        setActiveSection(
          sectionFromHash
        )

        setShowMobileMenu(false)
        setShowNotifications(false)

        window.scrollTo({
          top: 0,
          behavior: 'auto',
        })
      }

    const initialHashSection =
      getRawHashSection()
    if (
      !DASHBOARD_SECTIONS.includes(
        initialHashSection
      )
    ) {
      window.history.replaceState(
        window.history.state,
        '',
        `${window.location.pathname}${window.location.search}#dashboard`
      )

      setActiveSection(
        'dashboard'
      )
    }

    window.addEventListener(
      'hashchange',
      synchronizeSectionWithHash
    )

    return () => {
      window.removeEventListener(
        'hashchange',
        synchronizeSectionWithHash
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

  const renderSection = () => {
    const sharedProps = {
      t,
      data,
      language,
      user: currentUser,
      activities,
      projects,

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

                  <button
                    type="button"
                    onClick={() =>
                      setShowNotifications(
                        false
                      )
                    }
                    aria-label="Fermer les notifications"
                  >
                    ×
                  </button>
                </div>

                <div className="dash-notification-portal-list">
                  {notificationItems.length >
                  0 ? (
                    notificationItems.map(
                      (
                        notification,
                        index
                      ) => (
                        <div
                          className="dash-notification-row"
                          key={`${notification}-${index}`}
                        >
                          <strong>
                            {index + 1}
                          </strong>

                          <p>
                            {
                              notification
                            }
                          </p>
                        </div>
                      )
                    )
                  ) : (
                    <div className="dash-empty">
                      {language ===
                      'FR'
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
            aria-label={`Notifications : ${notificationItems.length}`}
          >
            <span
              className="dash-notification-icon"
              aria-hidden="true"
            >
              🔔
            </span>

            {notificationItems.length >
              0 && (
              <span className="dash-notification-badge">
                {
                  notificationItems.length
                }
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

          {/* <div className="dash-sidebar-card">
            <div className="dash-sidebar-avatar">
              {userInitials}
            </div>

            <h3>
              {
                currentUser.prenom
              }{' '}
              {currentUser.nom}
            </h3>

            <p>
              {t.waterAmbassador}
            </p>

            <small>
              {
                currentUser.niveau
              }
            </small>
          </div> */}

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