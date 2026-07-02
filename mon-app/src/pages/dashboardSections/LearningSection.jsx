function LearningSection({ t, data, setActiveSection }) {
  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">{t.learning.kicker}</p>
          <h1>{t.learning.title}</h1>
          <p>{t.learning.subtitle}</p>
        </div>
      </div>

      <div className="dash-grid-3">
        {data.modules.map((module) => (
          <article className="dash-card module-card" key={module.id}>
            <div
              className="module-image"
              style={{ backgroundImage: `url(${module.image})` }}
            />

            <div className="module-body">
              <div className="dash-card-top">
                <div>
                  <span className="dash-pill">{module.category}</span>
                  <h3>{module.title}</h3>
                </div>
                <span className="dash-pill gold">{module.points} pts</span>
              </div>

              <p>{module.explanation}</p>

              <div className="module-flow">
                <span>{t.learning.read}</span>
                <span>→</span>
                <span>{module.quiz}</span>
                <span>→</span>
                <span>{t.learning.challenge}</span>
                <span>→</span>
                <span>{t.learning.submit}</span>
              </div>

              <div className="dash-progress-track">
                <div className="dash-progress-fill" style={{ width: `${module.progress}%` }} />
              </div>

              <button
                type="button"
                className="dash-primary-btn"
                onClick={() => setActiveSection('challenges')}
              >
                {t.learning.start}
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

export default LearningSection
