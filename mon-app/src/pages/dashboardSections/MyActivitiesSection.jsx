function MyActivitiesSection({ t, activities, setActiveSection }) {
  const getStatusClass = (status) => {
    if (status === 'validated') return 'validated'
    if (status === 'rejected') return 'rejected'
    return 'pending'
  }

  const getStatusLabel = (status) => {
    return t.status[status] || t.status.pending
  }

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">{t.activities.kicker}</p>
          <h1>{t.activities.title}</h1>
          <p>{t.activities.subtitle}</p>
        </div>

        <button
          type="button"
          className="dash-primary-btn"
          onClick={() => setActiveSection('submit')}
        >
          + {t.menu.submit}
        </button>
      </div>

      {activities.length === 0 ? (
        <div className="dash-empty">
          {t.activities.empty}
        </div>
      ) : (
        <div className="activity-list">
          {activities.map((activity) => (
            <article
              className={`activity-item ${getStatusClass(activity.status)}`}
              key={activity.id}
            >
              <div className="dash-card-top">
                <div>
                  <h3>{activity.title || activity.challengeTitle}</h3>
                  <p>{activity.challengeTitle}</p>
                </div>
                <span className={`dash-pill ${activity.status === 'validated' ? 'green' : 'gold'}`}>
                  {getStatusLabel(activity.status)}
                </span>
              </div>

              <p>{activity.description}</p>

              <div className="challenge-meta">
                <span className="dash-pill">📍 {activity.place}</span>
                <span className="dash-pill">📅 {activity.date}</span>
                <span className="dash-pill">👥 {activity.people}</span>
                {activity.photoName && <span className="dash-pill">📷 {activity.photoName}</span>}
                {activity.videoName && <span className="dash-pill">🎥 {activity.videoName}</span>}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

export default MyActivitiesSection
