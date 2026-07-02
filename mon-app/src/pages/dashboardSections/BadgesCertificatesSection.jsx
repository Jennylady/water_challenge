function BadgesCertificatesSection({ t, data, user }) {
  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">{t.badges.kicker}</p>
          <h1>{t.badges.title}</h1>
          <p>{t.badges.subtitle}</p>
        </div>
      </div>

      <div className="dash-grid-4">
        {data.badges.map((badge) => (
          <article
            key={badge.title}
            className={`dash-card badge-big-card ${badge.unlocked ? 'unlocked' : 'locked'}`}
          >
            <div className="badge-icon-large">{badge.unlocked ? badge.icon : '🔒'}</div>
            <h3>{badge.title}</h3>
            <p>{badge.condition}</p>

            <div className="challenge-meta" style={{ justifyContent: 'center' }}>
              <span className={`dash-pill ${badge.unlocked ? 'green' : ''}`}>
                {badge.unlocked ? t.badges.unlocked : t.badges.locked}
              </span>
            </div>
          </article>
        ))}
      </div>

      <div className="dash-card">
        <div className="dash-card-top">
          <div>
            <span className="dash-pill gold">PDF</span>
            <h3>{t.badges.certificate}</h3>
          </div>
          <span className="dash-pill">{user.points} pts</span>
        </div>

        <p>{t.badges.certificateText}</p>

        <div className="dash-progress-track">
          <div className="dash-progress-fill" style={{ width: `${Math.min(user.progression, 100)}%` }} />
        </div>
      </div>
    </section>
  )
}

export default BadgesCertificatesSection
