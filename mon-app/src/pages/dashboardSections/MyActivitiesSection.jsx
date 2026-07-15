import { useCallback, useEffect, useMemo, useState } from 'react'

import { getApiErrorMessage, getMediaUrl } from '../../api/api'
import { challengesApi } from '../../api/services'

const normalizeStatus = (status) => {
  const value = String(status || '').toLowerCase()

  if (['validee', 'validated', 'accepted'].includes(value)) {
    return 'validated'
  }

  if (['refusee', 'rejected', 'refused'].includes(value)) {
    return 'rejected'
  }

  return 'pending'
}

const normalizeActivity = (activity) => ({
  ...activity,
  id: activity?.id,
  challengeTitle:
    activity?.defi_titre ||
    activity?.challengeTitle ||
    activity?.title ||
    'Challenge',
  description: activity?.rapport || activity?.description || '',
  place: activity?.lieu || activity?.place || '',
  date: activity?.date_activite || activity?.date || '',
  people:
    activity?.nombre_personnes_sensibilisees ?? activity?.people ?? 0,
  status: normalizeStatus(activity?.statut || activity?.status),
  rawStatus: activity?.statut || activity?.status || 'en_attente',
})

function MyActivitiesSection({ t, activities = [], setActiveSection }) {
  const [submissions, setSubmissions] = useState([])
  const [selectedSubmission, setSelectedSubmission] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingDetail, setIsLoadingDetail] = useState(false)
  const [isCancelling, setIsCancelling] = useState(false)
  const [error, setError] = useState('')


  const statusLabels = useMemo(
    () => ({
      pending: t?.status?.pending || 'En attente',
      validated: t?.status?.validated || 'Validée',
      rejected: t?.status?.rejected || 'Refusée',
    }),
    [t]
  )

  const loadSubmissions = useCallback(async () => {
    setIsLoading(true)
    setError('')

    try {
      const received = await challengesApi.listSubmissions()
      setSubmissions(
        (Array.isArray(received) ? received : []).map(normalizeActivity)
      )
    } catch (requestError) {
      console.error('Impossible de charger les soumissions :', requestError)
      setSubmissions([])
      setError(
        getApiErrorMessage(
          requestError,
          'Impossible de charger vos activités.'
        )
      )
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadSubmissions()
  }, [loadSubmissions])

  useEffect(() => {
    const refresh = () => loadSubmissions()
    window.addEventListener('waterchallenge:data-updated', refresh)

    return () => {
      window.removeEventListener('waterchallenge:data-updated', refresh)
    }
  }, [loadSubmissions])

  const openDetails = useCallback(async (submission) => {
    setSelectedSubmission(submission)
    setIsLoadingDetail(true)
    setError('')

    try {
      const detail = await challengesApi.getSubmission(submission.id)
      setSelectedSubmission(normalizeActivity(detail))
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          'Impossible de charger le détail de cette activité.'
        )
      )
    } finally {
      setIsLoadingDetail(false)
    }
  }, [])

  const cancelSubmission = useCallback(async () => {
    if (!selectedSubmission?.id || selectedSubmission.status !== 'pending') {
      return
    }

    setIsCancelling(true)
    setError('')

    try {
      await challengesApi.cancelSubmission(selectedSubmission.id)
      setSelectedSubmission(null)
      await loadSubmissions()
      window.dispatchEvent(
        new CustomEvent('waterchallenge:data-updated', {
          detail: { source: 'submission-cancelled' },
        })
      )
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          "Impossible d'annuler cette soumission."
        )
      )
    } finally {
      setIsCancelling(false)
    }
  }, [loadSubmissions, selectedSubmission])

  const getStatusClass = (status) =>
    status === 'validated'
      ? 'validated'
      : status === 'rejected'
        ? 'rejected'
        : 'pending'

  if (selectedSubmission) {
    const validation = selectedSubmission.validation
    const photos = Array.isArray(selectedSubmission.photos)
      ? selectedSubmission.photos
      : []

    return (
      <section className="dash-section">
        <div className="dash-section-heading">
          <div>
            <button
              type="button"
              className="dash-secondary-btn"
              onClick={() => setSelectedSubmission(null)}
            >
              ← Retour aux activités
            </button>
            <h1>{selectedSubmission.challengeTitle}</h1>
            <p>Détail de la soumission et état de validation.</p>
          </div>
        </div>

        {error && (
          <div className="activity-item rejected" role="alert">
            <h3>⚠️ Une erreur est survenue</h3>
            <p>{error}</p>
          </div>
        )}

        <article className={`activity-item ${getStatusClass(selectedSubmission.status)}`}>
          <div className="dash-card-top">
            <div>
              <h3>{selectedSubmission.challengeTitle}</h3>
              <p>{isLoadingDetail ? 'Chargement du détail…' : selectedSubmission.description}</p>
            </div>
            <span
              className={`dash-pill ${selectedSubmission.status === 'validated' ? 'green' : 'gold'}`}
            >
              {statusLabels[selectedSubmission.status]}
            </span>
          </div>

          <div className="challenge-meta">
            <span className="dash-pill">📍 {selectedSubmission.place || 'Non renseigné'}</span>
            <span className="dash-pill">📅 {selectedSubmission.date || '—'}</span>
            <span className="dash-pill">👥 {selectedSubmission.people}</span>
            <span className="dash-pill">📷 {photos.length}</span>
          </div>

          {photos.length > 0 && (
            <div className="activity-proof-grid">
              {photos.map((photo, index) => (
                <a
                  key={photo.id || index}
                  href={getMediaUrl(photo.image_url || photo.image)}
                  target="_blank"
                  rel="noreferrer"
                >
                  <img
                    src={getMediaUrl(photo.image_url || photo.image)}
                    alt={`Preuve ${index + 1}`}
                  />
                </a>
              ))}
            </div>
          )}

          {selectedSubmission.video_url && (
            <a
              className="dash-secondary-btn activity-video-link"
              href={getMediaUrl(selectedSubmission.video_url)}
              target="_blank"
              rel="noreferrer"
            >
              🎥 Consulter la vidéo
            </a>
          )}

          {validation && (
            <div className="activity-validation-box">
              <h3>Décision de validation</h3>
              <p>{validation.commentaire || 'Aucun commentaire.'}</p>
              <div className="challenge-meta">
                <span className="dash-pill green">
                  ⭐ {validation.points_attribues ?? 0} points
                </span>
                {validation.validateur_nom && (
                  <span className="dash-pill">👤 {validation.validateur_nom}</span>
                )}
              </div>
            </div>
          )}

          {selectedSubmission.status === 'pending' && (
            <button
              type="button"
              className="dash-secondary-btn activity-cancel-btn"
              disabled={isCancelling}
              onClick={cancelSubmission}
            >
              {isCancelling ? 'Annulation…' : 'Annuler cette soumission'}
            </button>
          )}
        </article>
      </section>
    )
  }

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <h1>{t?.activities?.title || 'Mes activités'}</h1>
          <p>{t?.activities?.subtitle || 'Suivez vos soumissions et leur validation.'}</p>
        </div>

        <button
          type="button"
          className="dash-primary-btn"
          onClick={() => setActiveSection('submit')}
        >
          + {t?.menu?.submit || 'Soumettre une activité'}
        </button>
      </div>

      {error && (
        <div className="activity-item rejected" role="alert">
          <h3>⚠️ Chargement incomplet</h3>
          <p>{error}</p>
          <button type="button" className="dash-secondary-btn" onClick={loadSubmissions}>
            Réessayer
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="dash-empty">Chargement de vos activités…</div>
      ) : submissions.length === 0 ? (
        <div className="dash-empty">
          {t?.activities?.empty || "Vous n'avez encore soumis aucune activité."}
        </div>
      ) : (
        <div className="activity-list">
          {submissions.map((activity) => (
            <article
              className={`activity-item ${getStatusClass(activity.status)}`}
              key={activity.id}
            >
              <div className="dash-card-top">
                <div>
                  <h3>{activity.challengeTitle}</h3>
                  <p>{activity.description}</p>
                </div>
                <span
                  className={`dash-pill ${activity.status === 'validated' ? 'green' : 'gold'}`}
                >
                  {statusLabels[activity.status]}
                </span>
              </div>

              <div className="challenge-meta">
                <span className="dash-pill">📍 {activity.place || '—'}</span>
                <span className="dash-pill">📅 {activity.date || '—'}</span>
                <span className="dash-pill">👥 {activity.people}</span>
                {Array.isArray(activity.photos) && (
                  <span className="dash-pill">📷 {activity.photos.length}</span>
                )}
              </div>

              <button
                type="button"
                className="dash-secondary-btn activity-detail-btn"
                onClick={() => openDetails(activity)}
              >
                Voir le détail
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

export default MyActivitiesSection
