import { useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'

import { getApiErrorMessage } from '../../api/api'
import {
  challengesApi,
  formationApi,
  rewardsApi,
} from '../../api/services'

const formatLevel = (level) => {
  const values = {
    debutant: 'Débutant',
    apprenti: 'Apprenti',
    actif: 'Actif',
    leader: 'Leader',
  }

  return values[String(level || '').toLowerCase()] || level || 'Tous niveaux'
}

function DashboardHome({ t, user, setActiveSection }) {
  const [progression, setProgression] = useState(Number(user?.progression || 0))
  const [statistics, setStatistics] = useState(null)
  const [badges, setBadges] = useState([])
  const [ongoingChallenges, setOngoingChallenges] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const loadDashboard = useCallback(async () => {
    setIsLoading(true)
    setError('')

    const results = await Promise.allSettled([
      formationApi.getProgression(),
      challengesApi.getStatistics(),
      rewardsApi.mine(),
      challengesApi.list({ statut: 'en_cours' }),
    ])

    const [progressionResult, statisticsResult, rewardsResult, challengesResult] = results
    const errors = []

    if (progressionResult.status === 'fulfilled') {
      setProgression(
        Number(progressionResult.value?.pourcentage_global ?? user?.progression ?? 0)
      )
    } else {
      errors.push(progressionResult.reason)
    }

    if (statisticsResult.status === 'fulfilled') {
      setStatistics(statisticsResult.value)
    } else {
      errors.push(statisticsResult.reason)
    }

    if (rewardsResult.status === 'fulfilled') {
      setBadges(rewardsResult.value.badges)
    } else {
      errors.push(rewardsResult.reason)
    }

    if (challengesResult.status === 'fulfilled') {
      setOngoingChallenges(
        (Array.isArray(challengesResult.value) ? challengesResult.value : []).slice(0, 4)
      )
    } else {
      errors.push(challengesResult.reason)
    }

    if (errors.length > 0) {
      setError(
        getApiErrorMessage(
          errors[0],
          'Certaines données du tableau de bord ne sont pas disponibles.'
        )
      )
    }

    setIsLoading(false)
  }, [user?.progression])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

  useEffect(() => {
    const refresh = () => loadDashboard()
    window.addEventListener('waterchallenge:data-updated', refresh)

    return () => {
      window.removeEventListener('waterchallenge:data-updated', refresh)
    }
  }, [loadDashboard])


  const stats = [
    {
      icon: '⭐',
      label: t?.home?.points || 'Points',
      value: statistics?.points ?? user?.points ?? 0,
    },
    {
      icon: '📈',
      label: t?.home?.progression || 'Progression',
      value: `${Math.round(progression)}%`,
    },
    {
      icon: '🏅',
      label: t?.home?.badges || 'Badges',
      value: badges.length,
    },
    {
      icon: '⏳',
      label: t?.home?.pending || 'En attente',
      value: statistics?.soumissions_en_attente ?? 0,
    },
  ]

  const displayChallenges = ongoingChallenges

  const getChallengeStars = (points) => {
    if (points >= 100) return 5
    if (points >= 50) return 4
    if (points >= 25) return 3
    return 2
  }

  return (
    <section className="dash-section">
      <div className="dash-hero-card dash-greeting-hero">
        <div className="dash-greeting-content">
          <p className="dash-kicker">{t?.home?.kicker}</p>
          <h2>
            {t?.home?.title || 'Bienvenue'}, {' '}
            <span className="dash-hero-name">{user?.prenom}</span>
          </h2>
          <p>{t?.home?.subtitle}</p>
        </div>

        <div className="dash-greeting-bottom">
          <div className="dash-greeting-progress">
            <span>
              {Math.round(progression)}% — {t?.waterAmbassador || 'Water Ambassador'}
            </span>
            <div className="dash-progress-track">
              <div
                className="dash-progress-fill"
                style={{ width: `${Math.min(Math.max(progression, 0), 100)}%` }}
              />
            </div>
          </div>

          <div className="dash-actions-row">
            <button
              type="button"
              className="dash-primary-btn"
              onClick={() => setActiveSection('learning')}
            >
              {t?.home?.continueLearning || 'Continuer la formation'}
            </button>
            <button
              type="button"
              className="dash-secondary-btn"
              onClick={() => setActiveSection('submit')}
            >
              {t?.home?.submitProof || 'Soumettre une preuve'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="dashboard-data-warning">
          <span>⚠️ {error}</span>
          <button type="button" onClick={loadDashboard}>Actualiser</button>
        </div>
      )}

      <div className="dash-grid-4">
        {stats.map((stat) => (
          <motion.div className="dash-stat-card" key={stat.label} whileHover={{ y: -4 }}>
            <div className="dash-stat-icon">{stat.icon}</div>
            <div className="dash-stat-info">
              <p>{stat.label}</p>
              <h3>{isLoading ? '…' : stat.value}</h3>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="dashboard-challenges-block">
        <div className="dash-card-top dashboard-challenges-title-row">
          <div>
            <h3>{t?.home?.ongoingTitle || 'Challenges en cours'}</h3>
          </div>
          <button
            type="button"
            className="dash-secondary-btn"
            onClick={() => setActiveSection('challenges')}
          >
            {t?.menu?.challenges || 'Challenges'}
          </button>
        </div>

        {displayChallenges.length === 0 ? (
          <div className="dash-empty">Aucun challenge en cours.</div>
        ) : (
          <div className="dashboard-challenge-grid">
            {displayChallenges.map((challenge) => {
              const points = Number(
                challenge?.points_recompense ?? challenge?.points ?? 0
              )
              const stars = getChallengeStars(points)

              return (
                <motion.article
                  className="dashboard-challenge-card"
                  key={challenge.id}
                  whileHover={{ y: -6, scale: 1.01 }}
                  transition={{ duration: 0.22 }}
                >
                  <div className="dashboard-challenge-top">
                    <span className="challenge-difficulty-pill">
                      {formatLevel(challenge?.niveau || challenge?.difficulty)}
                    </span>

                    <div className="challenge-stars" title={`${stars} étoiles`}>
                      <span>{'★'.repeat(stars)}</span>
                      <em>{'★'.repeat(5 - stars)}</em>
                    </div>
                  </div>

                  <h3>{challenge?.titre || challenge?.title}</h3>
                  <p>{challenge?.description || challenge?.objective}</p>

                  <div className="dashboard-challenge-bottom">
                    <span>{points} pts</span>
                    <span>{challenge?.duree_estimee || challenge?.duration || 'Libre'}</span>
                  </div>
                </motion.article>
              )
            })}
          </div>
        )}
      </div>
    </section>
  )
}

export default DashboardHome
