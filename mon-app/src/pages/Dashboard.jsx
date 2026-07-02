import { useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'framer-motion'
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
import { getDashboardData } from './dashboardSections/dashboardData'

function Dashboard({ user, onLogout }) {
  const [language, setLanguage] = useState('FR')
  const [activeSection, setActiveSection] = useState('dashboard')
  const [showNotifications, setShowNotifications] = useState(false)

  const [activities, setActivities] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('waterChallengeActivities')) || []
    } catch (error) {
      return []
    }
  })

  const [projects, setProjects] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('waterChallengeProjects')) || []
    } catch (error) {
      return []
    }
  })

  const data = useMemo(() => getDashboardData(language), [language])
  const t = data.text

  const currentUser = {
    prenom: user?.prenom || 'Water',
    nom: user?.nom || 'Ambassador',
    email: user?.email || 'ambassador@waterchallenge.mg',
    telephone: user?.telephone || '+261 XX XXX XXXX',
    faritra: user?.faritra || 'Madagascar',
    fivondronana: user?.fivondronana || 'Communauté locale',
    scoutType: user?.scoutType || 'Guide et Scout',
    section: user?.section || 'Mavo',
    position: user?.position || 'Beazina',
    niveau: user?.niveau || t.levelBeginner,
    badge: user?.badge || t.firstBadge,
    points: user?.points || 120,
    progression: user?.progression || 38,
  }

  const pendingCount = activities.filter((activity) => activity.status === 'pending').length
  const notificationItems = [
    ...data.notifications,
    ...(pendingCount > 0
      ? [
          language === 'FR'
            ? `${pendingCount} activité(s) en attente de validation.`
            : `${pendingCount} asa miandry fanamarinana.`,
        ]
      : []),
  ]

  const saveActivities = (nextActivities) => {
    setActivities(nextActivities)
    localStorage.setItem('waterChallengeActivities', JSON.stringify(nextActivities))
  }

  const saveProjects = (nextProjects) => {
    setProjects(nextProjects)
    localStorage.setItem('waterChallengeProjects', JSON.stringify(nextProjects))
  }

  const handleAddActivity = (activity) => {
    const nextActivity = {
      id: Date.now(),
      ...activity,
      status: 'pending',
      createdAt: new Date().toISOString(),
      author: `${currentUser.prenom} ${currentUser.nom}`,
    }

    saveActivities([nextActivity, ...activities])
    setActiveSection('activities')
  }

  const handleAddProject = (project) => {
    const nextProject = {
      id: Date.now(),
      ...project,
      progress: Number(project.progress || 0),
      photos: project.photos || '',
      createdAt: new Date().toISOString(),
      author: `${currentUser.prenom} ${currentUser.nom}`,
    }

    saveProjects([nextProject, ...projects])
  }

  const menuItems = [
    { id: 'dashboard', icon: '🏠', label: t.menu.dashboard },
    { id: 'learning', icon: '📚', label: t.menu.learning },
    { id: 'challenges', icon: '🏆', label: t.menu.challenges },
    { id: 'submit', icon: '📤', label: t.menu.submit },
    { id: 'activities', icon: '📁', label: t.menu.activities },
    { id: 'projects', icon: '🌍', label: t.menu.projects },
    { id: 'community', icon: '👥', label: t.menu.community },
    { id: 'badges', icon: '🏅', label: t.menu.badges },
    { id: 'profile', icon: '👤', label: t.menu.profile },
  ]

  const renderSection = () => {
    const sharedProps = {
      t,
      data,
      user: currentUser,
      activities,
      projects,
      setActiveSection,
    }

    switch (activeSection) {
      case 'learning':
        return <LearningSection {...sharedProps} />
      case 'challenges':
        return <ChallengesSection {...sharedProps} />
      case 'submit':
        return <SubmitActivitySection {...sharedProps} onAddActivity={handleAddActivity} />
      case 'activities':
        return <MyActivitiesSection {...sharedProps} />
      case 'projects':
        return <CommunityProjectsSection {...sharedProps} onAddProject={handleAddProject} />
      case 'community':
        return <CommunitySection {...sharedProps} />
      case 'badges':
        return <BadgesCertificatesSection {...sharedProps} />
      case 'profile':
        return <ProfileSection {...sharedProps} />
      default:
        return <DashboardHome {...sharedProps} />
    }
  }

  const notificationPortal = showNotifications && typeof document !== 'undefined'
    ? createPortal(
        <AnimatePresence>
          <motion.div
            className="dash-notification-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowNotifications(false)}
          >
            <motion.aside
              className="dash-notification-portal"
              initial={{ opacity: 0, y: -20, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -12, scale: 0.96 }}
              transition={{ duration: 0.24, ease: 'easeOut' }}
              onClick={(event) => event.stopPropagation()}
            >
              <div className="dash-notification-portal-head">
                <div>
                  <span>🔔</span>
                  <h3>{t.home.notificationsTitle}</h3>
                </div>
                <button type="button" onClick={() => setShowNotifications(false)}>
                  ×
                </button>
              </div>

              <div className="dash-notification-portal-list">
                {notificationItems.map((notification, index) => (
                  <div className="dash-notification-row" key={`${notification}-${index}`}>
                    <strong>{index + 1}</strong>
                    <p>{notification}</p>
                  </div>
                ))}
              </div>
            </motion.aside>
          </motion.div>
        </AnimatePresence>,
        document.body
      )
    : null

  return (
    <div className="dash-page">
      <motion.header
        className="dash-navbar dash-navbar-clean"
        initial={{ opacity: 0, y: -22 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease: 'easeOut' }}
      >
        <button
          type="button"
          className="dash-logo"
          onClick={() => setActiveSection('dashboard')}
        >
          <span className="dash-logo-mark">W</span>
          <span>Water Challenge</span>
        </button>

        <div className="dash-navbar-right">
          <button
            type="button"
            className="dash-notification-btn"
            onClick={() => setShowNotifications(true)}
            title="Notifications"
          >
            <span className="dash-notification-icon">🔔</span>
            <span className="dash-notification-badge">{notificationItems.length}</span>
          </button>

          <div className="dash-language">
            <button
              type="button"
              className={language === 'FR' ? 'active' : ''}
              onClick={() => setLanguage('FR')}
            >
              FR
            </button>
            <button
              type="button"
              className={language === 'MLG' ? 'active' : ''}
              onClick={() => setLanguage('MLG')}
            >
              MLG
            </button>
          </div>

          <div className="dash-mini-user">
            <span>{currentUser.prenom?.charAt(0)}{currentUser.nom?.charAt(0)}</span>
            <div>
              <strong>{currentUser.prenom}</strong>
              <small>{currentUser.niveau}</small>
            </div>
          </div>

          <button type="button" className="dash-logout" onClick={onLogout}>
            {t.logout}
          </button>
        </div>
      </motion.header>

      <div className="dash-shell dash-shell-wide">
        <aside className="dash-sidebar">
          <div className="dash-sidebar-card">
            <div className="dash-sidebar-avatar">
              {currentUser.prenom?.charAt(0)}{currentUser.nom?.charAt(0)}
            </div>
            {/* <h3>{currentUser.prenom} {currentUser.nom}</h3> */}
            <p>{t.waterAmbassador}</p>
          </div>

          <nav className="dash-menu">
            {menuItems.map((item) => (
              <button
                key={item.id}
                type="button"
                className={activeSection === item.id ? 'active' : ''}
                onClick={() => setActiveSection(item.id)}
              >
                <span>{item.icon}</span>
                {item.label}
              </button>
            ))}
          </nav>
        </aside>

        <main className="dash-content">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeSection}
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.32, ease: 'easeOut' }}
            >
              {renderSection()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {notificationPortal}
    </div>
  )
}

export default Dashboard
