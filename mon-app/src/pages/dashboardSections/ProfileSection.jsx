function ProfileSection({ t, user, activities, projects }) {
  const peopleTouched = activities.reduce((total, activity) => total + Number(activity.people || 0), 0)

  const personalInfo = [
    ['Nom', `${user.prenom} ${user.nom}`],
    ['Email', user.email],
    ['Téléphone', user.telephone],
    ['Région', user.faritra],
    ['District', user.fivondronana],
    ['Organisation', user.scoutType],
    ['Section', user.section],
    ['Position', user.position],
  ]

  const stats = [
    ['Points', user.points],
    ['Progression', `${user.progression}%`],
    ['Activités envoyées', activities.length],
    ['Projets créés', projects.length],
    ['Personnes touchées', peopleTouched],
    ['Badge actuel', user.badge],
  ]

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">{t.profile.kicker}</p>
          <h1>{t.profile.title}</h1>
          <p>{t.profile.subtitle}</p>
        </div>
      </div>

      <div className="dash-card profile-hero">
        <div className="profile-photo">
          {user.prenom?.charAt(0)}{user.nom?.charAt(0)}
        </div>

        <div>
          <h3>{user.prenom} {user.nom}</h3>
          <p>{t.waterAmbassador} — {user.niveau}</p>

          <div className="dash-progress-track">
            <div className="dash-progress-fill" style={{ width: `${user.progression}%` }} />
          </div>
        </div>
      </div>

      <div className="dash-grid-2">
        <div className="dash-card">
          <h3>{t.profile.personal}</h3>
          <div className="profile-info-grid">
            {personalInfo.map(([label, value]) => (
              <div className="profile-info-item" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="dash-card">
          <h3>{t.profile.stats}</h3>
          <div className="profile-info-grid">
            {stats.map(([label, value]) => (
              <div className="profile-info-item" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

export default ProfileSection
