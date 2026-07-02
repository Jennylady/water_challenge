import './BadgeCard.css';

export default function BadgeCard({ icon, title, description, unlocked, points }) {
  return (
    <div className={`badge-card${unlocked ? ' badge-card--unlocked' : ' badge-card--locked'}`}>
      <div className="badge-card__glow" />

      <div className="badge-card__icon-wrap">
        <div className={`badge-card__icon-ring${unlocked ? ' badge-card__icon-ring--active' : ''}`} />
        <span className="badge-card__icon" style={{ filter: unlocked ? 'none' : 'grayscale(1) opacity(0.4)' }}>
          {icon}
        </span>
        {unlocked && <div className="badge-card__sparkle">✨</div>}
      </div>

      <h4 className="badge-card__title">{title}</h4>
      <p className="badge-card__desc">{description}</p>

      <div className="badge-card__footer">
        {unlocked ? (
          <span className="badge-card__status badge-card__status--unlocked">
            ✅ Débloqué
          </span>
        ) : (
          <span className="badge-card__status badge-card__status--locked">
            🔒 {points} pts requis
          </span>
        )}
      </div>
    </div>
  );
}
