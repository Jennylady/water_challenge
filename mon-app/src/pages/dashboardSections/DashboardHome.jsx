import { motion } from 'framer-motion'

function DashboardHome({ t, data, user, activities, setActiveSection }) {
  const pendingCount = activities.filter((activity) => activity.status === 'pending').length
  const peopleTouched = activities.reduce((total, activity) => total + Number(activity.people || 0), 0)

  const stats = [
    { icon: '⭐', label: t.home.points, value: user.points },
    { icon: '📈', label: t.home.progression, value: `${user.progression}%` },
    { icon: '🏅', label: t.home.badges, value: data.badges.filter((badge) => badge.unlocked).length },
    { icon: '⏳', label: t.home.pending, value: pendingCount },
  ]

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
          <p className="dash-kicker">{t.home.kicker} </p>
          <h2>
            {t.home.title}, <span className="dash-hero-name">{user.prenom}</span>
          </h2>
          <p>{t.home.subtitle}</p>
        </div>

        <div className="dash-greeting-bottom">
          <div className="dash-greeting-progress">
            <span>{user.progression}% — {t.waterAmbassador}</span>
            <div className="dash-progress-track">
              <div className="dash-progress-fill" style={{ width: `${user.progression}%` }} />
            </div>
          </div>

          <div className="dash-actions-row">
            <button
              type="button"
              className="dash-primary-btn"
              onClick={() => setActiveSection('learning')}
            >
              {t.home.continueLearning}
            </button>
            <button
              type="button"
              className="dash-secondary-btn"
              onClick={() => setActiveSection('submit')}
            >
              {t.home.submitProof}
            </button>
          </div>
        </div>
      </div>

      <div className="dash-grid-4">
        {stats.map((stat) => (
          <motion.div
            className="dash-stat-card"
            key={stat.label}
            whileHover={{ y: -4 }}
          >
            <div className="dash-stat-icon">{stat.icon}</div>
            <div className="dash-stat-info">
              <p>{stat.label}</p>
              <h3>{stat.value}</h3>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="dashboard-challenges-block">
        <div className="dash-card-top dashboard-challenges-title-row">
          <div>
            <h3>{t.home.ongoingTitle}</h3>
          </div>
          <button
            type="button"
            className="dash-secondary-btn"
            onClick={() => setActiveSection('challenges')}
          >
            {t.menu.challenges}
          </button>
        </div>

        <div className="dashboard-challenge-grid">
          {data.challenges.map((challenge) => {
            const stars = getChallengeStars(challenge.points)

            return (
              <motion.article
                className="dashboard-challenge-card"
                key={challenge.id}
                whileHover={{ y: -6, scale: 1.01 }}
                transition={{ duration: 0.22 }}
              >
                <div className="dashboard-challenge-top">
                  <span className="challenge-difficulty-pill">
                    {challenge.difficulty}
                  </span>

                  <div className="challenge-stars" title={`${stars} étoiles`}>
                    <span>{'★'.repeat(stars)}</span>
                    <em>{'★'.repeat(5 - stars)}</em>
                  </div>
                </div>

                <h3>{challenge.title}</h3>
                <p>{challenge.objective}</p>

                <div className="dashboard-challenge-bottom">
                  <span>{challenge.points} pts</span>
                  <span>{challenge.duration}</span>
                </div>
              </motion.article>
            )
          })}
        </div>
      </div>

     
    </section>
  )
}

export default DashboardHome
