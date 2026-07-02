import BadgeCard from '../BadgeCard/BadgeCard';
import './ProgressSection.css';

const badges = [
  {
    id: 1,
    icon: '📨',
    title: 'Messager de l\'eau',
    description: 'Parle de l\'eau à 5 personnes autour de toi',
    unlocked: true,
    points: 0,
  },
  {
    id: 2,
    icon: '🌊',
    title: 'Gardien de la source',
    description: 'Accomplis 10 missions terrain sur le terrain',
    unlocked: true,
    points: 0,
  },
  {
    id: 3,
    icon: '🌿',
    title: 'Protecteur de la nature',
    description: 'Plante ou protège un espace naturel humide',
    unlocked: false,
    points: 1500,
  },
  {
    id: 4,
    icon: '🦸',
    title: 'Héros anti-gaspillage',
    description: 'Économise 50L d\'eau en une semaine',
    unlocked: false,
    points: 2000,
  },
  {
    id: 5,
    icon: '🔬',
    title: 'Explorateur aquatique',
    description: 'Analyse la qualité d\'une source d\'eau',
    unlocked: false,
    points: 2500,
  },
  {
    id: 6,
    icon: '🏆',
    title: 'Champion de l\'eau',
    description: 'Atteins le rang suprême et 5000 points',
    unlocked: false,
    points: 5000,
  },
];

const milestones = [
  { label: 'Recrue',     points: 0,    reached: true },
  { label: 'Éclaireur', points: 500,  reached: true },
  { label: 'Ranger',    points: 1500, reached: false },
  { label: 'Maître',    points: 3000, reached: false },
  { label: 'Légende',   points: 5000, reached: false },
];

export default function ProgressSection() {
  const currentPoints = 1240;
  const nextMilestone = milestones.find(m => m.points > currentPoints);
  const progressPct = nextMilestone
    ? Math.min((currentPoints / nextMilestone.points) * 100, 100)
    : 100;

  return (
    <section className="progress-section" id="badges">
      <div className="progress-section__inner">

        {/* Header */}
        <div className="progress-section__header">
          <div>
            <h2 className="progress-section__title">🏅 Mes Badges & Progression</h2>
            <p className="progress-section__subtitle">
              Débloque des badges en accomplissant des missions et en gagnant des points.
            </p>
          </div>
        </div>

        {/* Journey / Milestones */}
        <div className="progress-journey">
          <h3 className="progress-journey__label">Ton parcours scout</h3>
          <div className="progress-journey__track">
            <div
              className="progress-journey__fill"
              style={{ width: `${progressPct}%` }}
            />
            {milestones.map((m, i) => (
              <div
                key={m.label}
                className={`progress-journey__node${m.reached ? ' progress-journey__node--reached' : ''}`}
                style={{ left: `${(i / (milestones.length - 1)) * 100}%` }}
              >
                <div className="progress-journey__dot">
                  {m.reached ? '✓' : ''}
                </div>
                <span className="progress-journey__node-label">{m.label}</span>
                <span className="progress-journey__node-pts">{m.points > 0 ? `${m.points} pts` : 'Départ'}</span>
              </div>
            ))}
          </div>
          <div className="progress-journey__info">
            <span className="progress-journey__current">
              💧 <strong>{currentPoints.toLocaleString()} pts</strong>
            </span>
            {nextMilestone && (
              <span className="progress-journey__next">
                Prochain rang : <strong>{nextMilestone.label}</strong> ({nextMilestone.points} pts)
              </span>
            )}
          </div>
        </div>

        {/* Badges grid */}
        <div className="progress-section__badges">
          {badges.map((b, i) => (
            <div key={b.id} style={{ animationDelay: `${i * 0.08}s` }}>
              <BadgeCard {...b} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
