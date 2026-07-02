import { useState } from 'react'

function SubmitActivitySection({ t, data, onAddActivity }) {
  const [form, setForm] = useState({
    challengeId: data.challenges[0]?.id || '',
    title: '',
    date: '',
    place: '',
    people: '',
    description: '',
    photoName: '',
    videoName: '',
  })

  const [message, setMessage] = useState('')

  const selectedChallenge = data.challenges.find(
    (challenge) => String(challenge.id) === String(form.challengeId)
  )

  const handleChange = (event) => {
    const { name, value, files } = event.target

    if (files && files[0]) {
      setForm((previous) => ({
        ...previous,
        [name]: files[0].name,
      }))
      return
    }

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()

    onAddActivity({
      ...form,
      challengeTitle: selectedChallenge?.title || form.title,
      points: selectedChallenge?.points || 0,
    })

    setMessage(t.submit.saved)

    setForm({
      challengeId: data.challenges[0]?.id || '',
      title: '',
      date: '',
      place: '',
      people: '',
      description: '',
      photoName: '',
      videoName: '',
    })
  }

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">{t.submit.kicker}</p>
          <h1>{t.submit.title}</h1>
          <p>{t.submit.subtitle}</p>
        </div>
      </div>

      {message && (
        <div className="activity-item validated">
          <h3>✅ {message}</h3>
          <p>{t.submit.fileNote}</p>
        </div>
      )}

      <div className="dash-form-card">
        <form className="dash-form" onSubmit={handleSubmit}>
          <div className="dash-form-grid">
            <div className="dash-form-group full">
              <label>{t.submit.challenge}</label>
              <select
                name="challengeId"
                value={form.challengeId}
                onChange={handleChange}
                required
              >
                {data.challenges.map((challenge) => (
                  <option value={challenge.id} key={challenge.id}>
                    {challenge.title} — {challenge.points} pts
                  </option>
                ))}
              </select>
            </div>

            <div className="dash-form-group">
              <label>{t.submit.titleLabel}</label>
              <input
                type="text"
                name="title"
                value={form.title}
                onChange={handleChange}
                placeholder="Ex: Sensibilisation à l’école"
                required
              />
            </div>

            <div className="dash-form-group">
              <label>{t.submit.date}</label>
              <input
                type="date"
                name="date"
                value={form.date}
                onChange={handleChange}
                required
              />
            </div>

            <div className="dash-form-group">
              <label>{t.submit.place}</label>
              <input
                type="text"
                name="place"
                value={form.place}
                onChange={handleChange}
                placeholder="Ex: Fianarantsoa"
                required
              />
            </div>

            <div className="dash-form-group">
              <label>{t.submit.people}</label>
              <input
                type="number"
                min="0"
                name="people"
                value={form.people}
                onChange={handleChange}
                placeholder="Ex: 12"
                required
              />
            </div>

            <div className="dash-form-group">
              <label>{t.submit.photo}</label>
              <input
                type="file"
                name="photoName"
                accept="image/*"
                onChange={handleChange}
                required
              />
            </div>

            <div className="dash-form-group">
              <label>{t.submit.video}</label>
              <input
                type="file"
                name="videoName"
                accept="video/*"
                onChange={handleChange}
              />
            </div>

            <div className="dash-form-group full">
              <label>{t.submit.description}</label>
              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                placeholder="Décris ce que tu as fait, qui a participé, et l’impact observé..."
                required
              />
            </div>
          </div>

          <p className="dash-form-note">{t.submit.fileNote}</p>

          <button type="submit" className="dash-primary-btn">
            {t.submit.submitButton}
          </button>
        </form>
      </div>
    </section>
  )
}

export default SubmitActivitySection
