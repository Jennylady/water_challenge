function ChallengesSection({ t, data, setActiveSection }) {
  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">{t.challenges.kicker}</p>
          <h1>{t.challenges.title}</h1>
          <p>{t.challenges.subtitle}</p>
        </div>
      </div>

      <div className="dash-grid-2">
        {data.challenges.map((challenge) => (
          <article className="dash-card" key={challenge.id}>
            <div className="dash-card-top">
              <div>
                <span className="dash-pill">{challenge.category}</span>
                <h3>{challenge.title}</h3>
              </div>
              <span className="dash-pill gold">{challenge.points} pts</span>
            </div>

            <p>
              <strong>{t.challenges.objective} : </strong>
              {challenge.objective}
            </p>

            <div className="challenge-meta">
              <span className="dash-pill">{t.challenges.difficulty}: {challenge.difficulty}</span>
              <span className="dash-pill green">{t.challenges.duration}: {challenge.duration}</span>
            </div>

            <h3>{t.challenges.instructions}</h3>
            <ul className="challenge-instructions">
              {challenge.instructions.map((instruction) => (
                <li key={instruction}>{instruction}</li>
              ))}
            </ul>

            <button
              type="button"
              className="dash-primary-btn"
              onClick={() => setActiveSection('submit')}
            >
              {t.challenges.submit}
            </button>
          </article>
        ))}
      </div>
    </section>
  )
}

export default ChallengesSection
