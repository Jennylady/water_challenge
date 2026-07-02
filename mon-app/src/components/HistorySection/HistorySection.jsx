import './HistorySection.css';

const historyData = [
  {
    id: 1,
    mission: 'Ferme le robinet pendant le brossage',
    category: 'Personnel',
    categoryIcon: '🪥',
    date: '26 mai 2026',
    points: 50,
    status: 'completed',
  },
  {
    id: 2,
    mission: 'Parle à un ami d\'une économie d\'eau',
    category: 'Sensibilisation',
    categoryIcon: '📢',
    date: '25 mai 2026',
    points: 80,
    status: 'completed',
  },
  {
    id: 3,
    mission: 'Collecte d\'eau de pluie pour le jardin',
    category: 'Terrain',
    categoryIcon: '🌿',
    date: '24 mai 2026',
    points: 120,
    status: 'completed',
  },
  {
    id: 4,
    mission: 'Analyse de la consommation familiale',
    category: 'Personnel',
    categoryIcon: '🪥',
    date: '23 mai 2026',
    points: 90,
    status: 'completed',
  },
  {
    id: 5,
    mission: 'Atelier sensibilisation à l\'école',
    category: 'Sensibilisation',
    categoryIcon: '📢',
    date: '22 mai 2026',
    points: 150,
    status: 'completed',
  },
  {
    id: 6,
    mission: 'Nettoyage d\'une rivière locale',
    category: 'Terrain',
    categoryIcon: '🌿',
    date: '20 mai 2026',
    points: 200,
    status: 'completed',
  },
];

const categoryColors = {
  Personnel:       'blue',
  Sensibilisation: 'purple',
  Terrain:         'green',
};

export default function HistorySection() {
  const totalPoints = historyData.reduce((s, m) => s + m.points, 0);

  return (
    <section className="history-section" id="historique">
      <div className="history-section__inner">
        <div className="history-section__header">
          <div>
            <h2 className="history-section__title">📋 Historique des missions</h2>
            <p className="history-section__subtitle">
              Retrouve toutes tes missions accomplies et les points gagnés.
            </p>
          </div>
          <div className="history-section__total">
            <span className="history-section__total-icon">💧</span>
            <div>
              <div className="history-section__total-val">{totalPoints} pts</div>
              <div className="history-section__total-label">Points cumulés</div>
            </div>
          </div>
        </div>

        <div className="history-timeline">
          {historyData.map((item, index) => (
            <div
              key={item.id}
              className="history-item"
              style={{ animationDelay: `${index * 0.07}s` }}
            >
              {/* Timeline dot */}
              <div className="history-item__line">
                <div className={`history-item__dot history-item__dot--${categoryColors[item.category]}`}>
                  {item.categoryIcon}
                </div>
                {index < historyData.length - 1 && <div className="history-item__connector" />}
              </div>

              {/* Card */}
              <div className="history-item__card">
                <div className="history-item__card-left">
                  <span className={`history-item__cat history-item__cat--${categoryColors[item.category]}`}>
                    {item.category}
                  </span>
                  <h4 className="history-item__mission">{item.mission}</h4>
                  <span className="history-item__date">📅 {item.date}</span>
                </div>
                <div className="history-item__card-right">
                  <div className="history-item__points">
                    <span className="history-item__points-val">+{item.points}</span>
                    <span className="history-item__points-label">pts</span>
                  </div>
                  <span className="history-item__check">✅</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="history-section__footer">
          <button className="history-section__load-btn">
            Voir toutes les missions →
          </button>
        </div>
      </div>
    </section>
  );
}
