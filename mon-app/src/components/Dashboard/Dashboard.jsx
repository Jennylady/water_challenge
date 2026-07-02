import './Dashboard.css';

const stats = [
  {
    id: 'points',
    icon: '💧',
    value: '1 240',
    label: 'Points eau',
    sub: '+120 cette semaine',
    color: 'blue',
    trend: 'up',
  },
  {
    id: 'rang',
    icon: '⚜️',
    value: 'Éclaireur',
    label: 'Rang scout',
    sub: '3 rangs disponibles',
    color: 'gold',
    trend: 'neutral',
  },
  {
    id: 'serie',
    icon: '🔥',
    value: '7 jours',
    label: 'Série quotidienne',
    sub: 'Record personnel !',
    color: 'orange',
    trend: 'up',
  },
  {
    id: 'badge',
    icon: '🏅',
    value: 'Messager',
    label: 'Badge actuel',
    sub: '2 badges restants',
    color: 'green',
    trend: 'neutral',
  },
];

function StatCard({ icon, value, label, sub, color, trend }) {
  return (
    <div className={`stat-card stat-card--${color}`}>
      <div className="stat-card__header">
        <div className={`stat-card__icon-wrap stat-card__icon-wrap--${color}`}>
          <span className="stat-card__icon">{icon}</span>
        </div>
        {trend === 'up' && <span className="stat-card__trend">↑</span>}
      </div>
      <div className="stat-card__value">{value}</div>
      <div className="stat-card__label">{label}</div>
      <div className="stat-card__sub">{sub}</div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <section className="dashboard" id="dashboard">
      <div className="dashboard__inner">
        <div className="dashboard__header">
          <div className="dashboard__greeting">
            <span className="dashboard__avatar">🧑‍🦱</span>
            <div>
              <h2 className="dashboard__title">Bonjour, Scout Thomas ! 👋</h2>
              <p className="dashboard__date">Mercredi 26 mai 2026 · Patrouille Rivière</p>
            </div>
          </div>
          <div className="dashboard__level">
            <div className="dashboard__level-badge">⚜️ Niveau 5</div>
            <div className="dashboard__level-bar">
              <div className="dashboard__level-fill" style={{ width: '68%' }} />
            </div>
            <span className="dashboard__level-text">68% vers Niveau 6</span>
          </div>
        </div>

        <div className="dashboard__grid">
          {stats.map(s => (
            <StatCard key={s.id} {...s} />
          ))}
        </div>

        {/* Quick actions */}
        <div className="dashboard__actions">
          <h3 className="dashboard__section-title">⚡ Actions rapides</h3>
          <div className="dashboard__actions-row">
            <button className="dashboard__action-btn">
              <span>🎯</span>
              <span>Défi du jour</span>
            </button>
            <button className="dashboard__action-btn">
              <span>📋</span>
              <span>Mes missions</span>
            </button>
            <button className="dashboard__action-btn">
              <span>🏅</span>
              <span>Mes badges</span>
            </button>
            <button className="dashboard__action-btn">
              <span>👥</span>
              <span>Ma patrouille</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
