import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import axios from 'axios'
import {
  motion,
  AnimatePresence,
} from 'framer-motion'
import './ProfileSection.css'

// Ajuste si besoin selon ton client axios / stockage du token
const API_BASE_URL =
  import.meta.env.VITE_API_URL || ''

function getAuthToken() {
  return (
    localStorage.getItem('access') ||
    localStorage.getItem('accessToken') ||
    ''
  )
}

function toDateInputValue(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toISOString().slice(0, 10)
}

function ProfileSection({
  t,
  data,
  language = 'FR',
  user,
  activities = [],
  projects = [],
  setActiveSection,
  onProfileUpdate,
}) {
  const labels = useMemo(() => {
    if (language === 'MLG') {
      return {
        kicker: 'Kaontiko',
        title: 'Ny mombamomba ahy',
        subtitle:
          'Jereo ny mombamomba anao sy ny fandrosoanao ao amin’ny Water Challenge.',
        ambassador: 'Water Ambassador',
        personalInfo: 'Mombamomba manokana',
        progress: 'Fandrosoana',
        firstName: 'Anarana',
        lastName: 'Fanampin’anarana',
        fullName: 'Anarana feno',
        email: 'Adiresy mailaka',
        phone: 'Laharana finday',
        birthDate: 'Daty nahaterahana',
        region: 'Faritra',
        community: 'Fivondronana',
        scoutType: 'Karazana skoto',
        section: 'Sampana',
        position: 'Andraikitra',
        role: 'Anjara',
        level: 'Ambaratonga',
        badge: 'Badge',
        points: 'Isa',
        progression: 'Fandrosoana',
        activities: 'Asa nalefa',
        projects: 'Tetikasa',
        accountStatus: 'Toetry ny kaonty',
        emailStatus: 'Fanamarinana mailaka',
        active: 'Miasa',
        inactive: 'Tsy miasa',
        verified: 'Voamarina',
        notVerified: 'Tsy mbola voamarina',
        memberSince: 'Mpikambana nanomboka',
        unavailable: 'Tsy voafaritra',
        viewActivities: 'Hijery ny asako',
        viewBadges: 'Hijery ny badge-ko',
        edit: 'Ovay',
        save: 'Tehirizo',
        saving: 'Mitehirizina...',
        cancel: 'Aoka',
        successMsg: 'Voatahiry soa aman-tsara ny fanovana.',
        errorMsg: 'Nisy olana. Andramo indray azafady.',
      }
    }

    return {
      kicker: 'Mon compte',
      title: 'Mon profil',
      subtitle:
        'Consultez vos informations personnelles et suivez votre progression dans Water Challenge.',
      ambassador: 'Water Ambassador',
      personalInfo: 'Informations personnelles',
      progress: 'Ma progression',
      firstName: 'Prénom',
      lastName: 'Nom',
      fullName: 'Nom complet',
      email: 'Adresse email',
      phone: 'Téléphone',
      birthDate: 'Date de naissance',
      region: 'Faritra',
      community: 'Fivondronana',
      scoutType: 'Type de scout',
      section: 'Section',
      position: 'Position',
      role: 'Rôle',
      level: 'Niveau',
      badge: 'Badge actuel',
      points: 'Points',
      progression: 'Progression',
      activities: 'Activités envoyées',
      projects: 'Projets communautaires',
      accountStatus: 'État du compte',
      emailStatus: 'Vérification email',
      active: 'Actif',
      inactive: 'Inactif',
      verified: 'Vérifié',
      notVerified: 'Non vérifié',
      memberSince: 'Membre depuis',
      unavailable: 'Non renseigné',
      viewActivities: 'Voir mes activités',
      viewBadges: 'Voir mes badges',
      edit: 'Modifier',
      save: 'Enregistrer',
      saving: 'Enregistrement...',
      cancel: 'Annuler',
      successMsg: 'Vos informations ont été mises à jour avec succès.',
      errorMsg: 'Une erreur est survenue. Veuillez réessayer.',
    }
  }, [language])

  // Copie locale de l'utilisateur, mise à jour après un PATCH réussi
  const [localUser, setLocalUser] = useState(user || {})

  useEffect(() => {
    setLocalUser(user || {})
  }, [user])

  const safeUser = localUser || {}

  const fullName =
    `${safeUser.prenom || ''} ${safeUser.nom || ''}`.trim() ||
    labels.unavailable

  const initials = useMemo(() => {
    const firstInitial =
      safeUser.prenom
        ?.trim()
        ?.charAt(0)
        ?.toUpperCase() || 'W'

    const lastInitial =
      safeUser.nom
        ?.trim()
        ?.charAt(0)
        ?.toUpperCase() || 'A'

    return `${firstInitial}${lastInitial}`
  }, [
    safeUser.prenom,
    safeUser.nom,
  ])

  const progression = Math.min(
    100,
    Math.max(
      0,
      Number(
        safeUser.progression || 0
      )
    )
  )

  const points =
    Number(
      safeUser.points || 0
    )

  const activityCount =
    Array.isArray(activities)
      ? activities.length
      : 0

  const projectCount =
    Array.isArray(projects)
      ? projects.length
      : 0

  const formatDate = (
    value
  ) => {
    if (!value) {
      return labels.unavailable
    }

    const date =
      new Date(value)

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return value
    }

    return new Intl.DateTimeFormat(
      language === 'MLG'
        ? 'mg-MG'
        : 'fr-FR',
      {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
      }
    ).format(date)
  }

  // Champs modifiables via le formulaire d'édition
  const editableFields = [
    { key: 'prenom', label: labels.firstName, type: 'text' },
    { key: 'nom', label: labels.lastName, type: 'text' },
    { key: 'email', label: labels.email, type: 'email' },
    { key: 'telephone', label: labels.phone, type: 'tel' },
    { key: 'birthDate', label: labels.birthDate, type: 'date' },
    { key: 'faritra', label: labels.region, type: 'text' },
    { key: 'fivondronana', label: labels.community, type: 'text' },
  ]

  // Champs affichés en lecture seule (non modifiables ici)
  const readonlyItems = [
    { label: labels.scoutType, value: safeUser.scoutType },
    { label: labels.section, value: safeUser.section },
    { label: labels.position, value: safeUser.position },
    { label: labels.role, value: safeUser.role },
  ]

  const informationItems = [
    { label: labels.fullName, value: fullName },
    { label: labels.email, value: safeUser.email || labels.unavailable },
    { label: labels.phone, value: safeUser.telephone || labels.unavailable },
    { label: labels.birthDate, value: formatDate(safeUser.birthDate) },
    { label: labels.region, value: safeUser.faritra || labels.unavailable },
    { label: labels.community, value: safeUser.fivondronana || labels.unavailable },
    ...readonlyItems.map((item) => ({
      label: item.label,
      value: item.value || labels.unavailable,
      readonly: true,
    })),
  ]

  const openSection = (
    sectionId
  ) => {
    if (
      typeof setActiveSection ===
      'function'
    ) {
      setActiveSection(
        sectionId
      )
    }
  }

  // ---- Edition du profil ----
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({})
  const [fieldErrors, setFieldErrors] = useState({})
  const [formMessage, setFormMessage] = useState({ type: null, text: '' })
  const [saving, setSaving] = useState(false)

  const startEditing = () => {
    setFormData({
      prenom: safeUser.prenom || '',
      nom: safeUser.nom || '',
      email: safeUser.email || '',
      telephone: safeUser.telephone || '',
      birthDate: toDateInputValue(safeUser.birthDate),
      faritra: safeUser.faritra || '',
      fivondronana: safeUser.fivondronana || '',
    })
    setFieldErrors({})
    setFormMessage({ type: null, text: '' })
    setIsEditing(true)
  }

  const cancelEditing = () => {
    setIsEditing(false)
    setFieldErrors({})
    setFormMessage({ type: null, text: '' })
  }

  const handleChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }))

    setFieldErrors((prev) => {
      if (!prev?.[key]) return prev
      const next = { ...prev }
      delete next[key]
      return next
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    setSaving(true)
    setFieldErrors({})
    setFormMessage({ type: null, text: '' })

    try {
      const response = await axios.patch(
        `${API_BASE_URL}/auth/me/profile/update/`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${getAuthToken()}`,
          },
        }
      )

      const updatedUser =
        response?.data?.user ||
        response?.data?.data ||
        { ...safeUser, ...formData }

      setLocalUser(updatedUser)

      if (typeof onProfileUpdate === 'function') {
        onProfileUpdate(updatedUser)
      }

      setFormMessage({
        type: 'success',
        text: response?.data?.message || labels.successMsg,
      })
      setIsEditing(false)
    } catch (error) {
      const responseData = error?.response?.data

      setFieldErrors(responseData?.errors || {})
      setFormMessage({
        type: 'error',
        text: responseData?.message || labels.errorMsg,
      })
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">
            {labels.kicker}
          </p>

          <h1>
            {labels.title}
          </h1>

          <p>
            {labels.subtitle}
          </p>
        </div>
      </div>

      <motion.article
        className="dash-card profile-hero"
        initial={{
          opacity: 0,
          y: 18,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          duration: 0.35,
          ease: 'easeOut',
        }}
      >
        <div
          className="profile-photo"
          aria-label={
            fullName
          }
        >
          {initials}
        </div>

        <div>
          <span className="dash-pill">
            {labels.ambassador}
          </span>

          <h2 className="dash-section-title">
            {fullName}
          </h2>

          <p>
            {safeUser.email ||
              labels.unavailable}
          </p>

          <div className="challenge-meta">
            <span className="dash-pill gold">
              🏅{' '}
              {safeUser.badge ||
                labels.unavailable}
            </span>

            <span className="dash-pill green">
              ⭐ {points}{' '}
              {labels.points}
            </span>

            <span className="dash-pill">
              🎯{' '}
              {safeUser.niveau ||
                labels.unavailable}
            </span>
          </div>
        </div>
      </motion.article>

      <div className="dash-grid-2">
        <motion.article
          className="dash-card"
          initial={{
            opacity: 0,
            y: 18,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.35,
            delay: 0.05,
            ease: 'easeOut',
          }}
        >
          <div className="dash-card-top">
            <div>
              <span className="dash-pill">
                👤
              </span>

              <h3>
                {
                  labels.personalInfo
                }
              </h3>
            </div>

            {!isEditing && (
              <button
                type="button"
                className="profile-edit-toggle-btn"
                onClick={startEditing}
              >
                ✏️ {labels.edit}
              </button>
            )}
          </div>

          <AnimatePresence>
            {formMessage.text && !isEditing && (
              <motion.p
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className={`profile-form-note profile-form-note--${formMessage.type}`}
              >
                {formMessage.text}
              </motion.p>
            )}
          </AnimatePresence>

          {!isEditing ? (
            <div className="profile-info-list">
              {informationItems.map((item) => (
                <div
                  className={`profile-info-row${
                    item.readonly ? ' profile-info-row--readonly' : ''
                  }`}
                  key={item.label}
                >
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          ) : (
            <form
              className="profile-edit-form"
              onSubmit={handleSubmit}
            >
              {formMessage.text && (
                <p
                  className={`profile-form-note profile-form-note--${formMessage.type}`}
                >
                  {formMessage.text}
                </p>
              )}

              <div className="profile-edit-grid">
                {editableFields.map((field) => (
                  <label
                    className="profile-edit-field"
                    key={field.key}
                  >
                    <span>{field.label}</span>

                    <input
                      type={field.type}
                      value={formData[field.key] || ''}
                      onChange={(e) =>
                        handleChange(field.key, e.target.value)
                      }
                    />

                    {fieldErrors[field.key] && (
                      <span className="profile-field-error">
                        {Array.isArray(fieldErrors[field.key])
                          ? fieldErrors[field.key].join(' ')
                          : String(fieldErrors[field.key])}
                      </span>
                    )}
                  </label>
                ))}
              </div>

              <div className="dash-actions-row">
                <button
                  type="submit"
                  className="dash-primary-btn"
                  disabled={saving}
                >
                  {saving ? labels.saving : labels.save}
                </button>

                <button
                  type="button"
                  className="dash-light-btn"
                  onClick={cancelEditing}
                  disabled={saving}
                >
                  {labels.cancel}
                </button>
              </div>
            </form>
          )}
        </motion.article>

        <motion.article
          className="dash-card"
          initial={{
            opacity: 0,
            y: 18,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.35,
            delay: 0.1,
            ease: 'easeOut',
          }}
        >
          <div className="dash-card-top">
            <div>
              <span className="dash-pill gold">
                📈
              </span>

              <h3>
                {labels.progress}
              </h3>
            </div>

            <span className="dash-pill green">
              {progression}%
            </span>
          </div>

          <div className="dash-progress">
            <div
              style={{
                width:
                  `${progression}%`,
              }}
            />
          </div>

          <div className="profile-info-grid profile-info-grid--stats">
            <div className="profile-info-item">
              <span>
                {labels.level}
              </span>

              <strong>
                {safeUser.niveau ||
                  labels.unavailable}
              </strong>
            </div>

            <div className="profile-info-item">
              <span>
                {labels.badge}
              </span>

              <strong>
                {safeUser.badge ||
                  labels.unavailable}
              </strong>
            </div>

            <div className="profile-info-item">
              <span>
                {labels.points}
              </span>

              <strong>
                {points}
              </strong>
            </div>

            <div className="profile-info-item">
              <span>
                {
                  labels.progression
                }
              </span>

              <strong>
                {progression}%
              </strong>
            </div>

            <div className="profile-info-item">
              <span>
                {labels.activities}
              </span>

              <strong>
                {activityCount}
              </strong>
            </div>

            <div className="profile-info-item">
              <span>
                {labels.projects}
              </span>

              <strong>
                {projectCount}
              </strong>
            </div>
          </div>

          <div className="dash-actions-row">
            <button
              type="button"
              className="dash-primary-btn"
              onClick={() =>
                openSection(
                  'activities'
                )
              }
            >
              {
                labels.viewActivities
              }
            </button>

            <button
              type="button"
              className="dash-light-btn"
              onClick={() =>
                openSection(
                  'badges'
                )
              }
            >
              {labels.viewBadges}
            </button>
          </div>
        </motion.article>
      </div>
    </section>
  )
}

export default ProfileSection