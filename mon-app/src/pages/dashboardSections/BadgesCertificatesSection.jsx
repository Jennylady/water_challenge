import { useCallback, useEffect, useState } from 'react'

import { getApiErrorMessage, getMediaUrl } from '../../api/api'
import { rewardsApi } from '../../api/services'

const getBadgeIcon = (name) => {
  const normalized = String(name || '').toLowerCase()

  if (normalized.includes('leader')) return '👑'
  if (normalized.includes('protecteur')) return '🛡️'
  if (normalized.includes('actif')) return '🌊'
  if (normalized.includes('goutte')) return '💧'
  return '🏅'
}

function BadgesCertificatesSection({ t, user }) {
  const [badges, setBadges] = useState([])
  const [certificates, setCertificates] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const loadRewards = useCallback(async () => {
    setIsLoading(true)
    setError('')

    try {
      const rewards = await rewardsApi.mine()
      setBadges(rewards.badges)
      setCertificates(rewards.certificats)
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          'Impossible de charger vos badges et certificats.'
        )
      )
      setBadges([])
      setCertificates([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadRewards()
  }, [loadRewards])

  useEffect(() => {
    const refresh = () => loadRewards()
    window.addEventListener('waterchallenge:data-updated', refresh)

    return () => {
      window.removeEventListener('waterchallenge:data-updated', refresh)
    }
  }, [loadRewards])

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">{t?.badges?.kicker || 'Récompenses'}</p>
          <h1>{t?.badges?.title || 'Badges et certificats'}</h1>
          <p>
            {t?.badges?.subtitle ||
              'Retrouvez les récompenses obtenues grâce à votre progression.'}
          </p>
        </div>

        <button type="button" className="dash-secondary-btn" onClick={loadRewards}>
          Actualiser
        </button>
      </div>

      {error && (
        <div className="activity-item rejected" role="alert">
          <h3>⚠️ Chargement impossible</h3>
          <p>{error}</p>
        </div>
      )}

      {isLoading ? (
        <div className="dash-empty">Chargement de vos récompenses…</div>
      ) : badges.length === 0 ? (
        <div className="dash-empty">
          Aucun badge obtenu pour le moment. Continuez les modules et les challenges.
        </div>
      ) : (
        <div className="dash-grid-4">
          {badges.map((badge) => (
            <article key={badge.id} className="dash-card badge-big-card unlocked">
              <div className="badge-icon-large">{getBadgeIcon(badge.nom)}</div>
              <h3>{badge.nom}</h3>
              <p>
                {badge.module
                  ? `Obtenu grâce au module ${badge.module}.`
                  : 'Badge obtenu grâce à votre progression.'}
              </p>

              <div className="challenge-meta" style={{ justifyContent: 'center' }}>
                <span className="dash-pill green">
                  {badge.obtenu_le
                    ? `Obtenu le ${new Date(badge.obtenu_le).toLocaleDateString('fr-FR')}`
                    : t?.badges?.unlocked || 'Débloqué'}
                </span>
              </div>
            </article>
          ))}
        </div>
      )}

      <div className="dash-card rewards-certificates-card">
        <div className="dash-card-top">
          <div>
            <span className="dash-pill gold">PDF</span>
            <h3>{t?.badges?.certificate || 'Mes certificats'}</h3>
          </div>
          <span className="dash-pill">{user?.points ?? 0} pts</span>
        </div>

        <p>
          {certificates.length > 0
            ? `${certificates.length} certificat(s) disponible(s).`
            : t?.badges?.certificateText ||
              'Les certificats apparaîtront ici dès qu’ils seront délivrés.'}
        </p>

        {certificates.length > 0 && (
          <div className="certificate-list">
            {certificates.map((certificate) => (
              <article className="certificate-list__item" key={certificate.id}>
                <div>
                  <strong>{certificate.titre}</strong>
                  <span>
                    {certificate.niveau || 'Tous niveaux'}
                    {certificate.delivre_le
                      ? ` • ${new Date(certificate.delivre_le).toLocaleDateString('fr-FR')}`
                      : ''}
                  </span>
                </div>

                {certificate.fichier ? (
                  <a
                    className="dash-primary-btn"
                    href={getMediaUrl(certificate.fichier)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Télécharger
                  </a>
                ) : (
                  <span className="dash-pill">Fichier indisponible</span>
                )}
              </article>
            ))}
          </div>
        )}

        <div className="dash-progress-track">
          <div
            className="dash-progress-fill"
            style={{ width: `${Math.min(Number(user?.progression || 0), 100)}%` }}
          />
        </div>
      </div>
    </section>
  )
}

export default BadgesCertificatesSection
