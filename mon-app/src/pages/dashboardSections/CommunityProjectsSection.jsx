import { useState } from 'react'

function CommunityProjectsSection({ t, projects, onAddProject }) {
  const [form, setForm] = useState({
    name: '',
    objective: '',
    description: '',
    date: '',
    place: '',
    progress: '',
    photos: '',
  })

  const handleChange = (event) => {
    const { name, value } = event.target

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    onAddProject(form)

    setForm({
      name: '',
      objective: '',
      description: '',
      date: '',
      place: '',
      progress: '',
      photos: '',
    })
  }

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">{t.projects.kicker}</p>
          <h1>{t.projects.title}</h1>
          <p>{t.projects.subtitle}</p>
        </div>
      </div>

      <div className="dash-grid-2">
        <div className="dash-form-card">
          <form className="dash-form" onSubmit={handleSubmit}>
            <div className="dash-form-grid">
              <div className="dash-form-group">
                <label>{t.projects.name}</label>
                <input
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="Ex: Water Club School"
                  required
                />
              </div>

              <div className="dash-form-group">
                <label>{t.projects.objective}</label>
                <input
                  name="objective"
                  value={form.objective}
                  onChange={handleChange}
                  placeholder="Ex: Sensibiliser 100 élèves"
                  required
                />
              </div>

              <div className="dash-form-group">
                <label>{t.projects.date}</label>
                <input
                  type="date"
                  name="date"
                  value={form.date}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="dash-form-group">
                <label>{t.projects.place}</label>
                <input
                  name="place"
                  value={form.place}
                  onChange={handleChange}
                  placeholder="Ex: Antananarivo"
                  required
                />
              </div>

              <div className="dash-form-group">
                <label>{t.projects.progress}</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  name="progress"
                  value={form.progress}
                  onChange={handleChange}
                  placeholder="0"
                  required
                />
              </div>

              <div className="dash-form-group">
                <label>{t.projects.photos}</label>
                <input
                  name="photos"
                  value={form.photos}
                  onChange={handleChange}
                  placeholder="Lien photo ou note"
                />
              </div>

              <div className="dash-form-group full">
                <label>{t.projects.description}</label>
                <textarea
                  name="description"
                  value={form.description}
                  onChange={handleChange}
                  placeholder="Décris les étapes, les personnes impliquées et l’impact attendu..."
                  required
                />
              </div>
            </div>

            <button type="submit" className="dash-primary-btn">
              {t.projects.create}
            </button>
          </form>
        </div>

        <div className="dash-card">
          <h3>{t.projects.existing}</h3>

          {projects.length === 0 ? (
            <div className="dash-empty">{t.projects.empty}</div>
          ) : (
            <div className="activity-list">
              {projects.map((project) => (
                <article className="activity-item validated" key={project.id}>
                  <div className="dash-card-top">
                    <div>
                      <h3>{project.name}</h3>
                      <p>{project.objective}</p>
                    </div>
                    <span className="dash-pill green">{project.progress}%</span>
                  </div>

                  <p>{project.description}</p>

                  <div className="dash-progress-track">
                    <div className="dash-progress-fill" style={{ width: `${project.progress}%` }} />
                  </div>

                  <div className="challenge-meta">
                    <span className="dash-pill">📍 {project.place}</span>
                    <span className="dash-pill">📅 {project.date}</span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

export default CommunityProjectsSection
