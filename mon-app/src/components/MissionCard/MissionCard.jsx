import { useState } from 'react';
import './MissionCard.css';

const categoryMeta = {
  Personnel:       { icon: '🪥', color: 'blue',   label: 'Personnel' },
  Sensibilisation: { icon: '📢', color: 'purple', label: 'Sensibilisation' },
  Terrain:         { icon: '🌿', color: 'green',  label: 'Terrain' },
};

export default function MissionCard({
  title,
  category,
  description,
  points,
  difficulty = 'Facile',
  duration = '5 min',
  completed = false,
  onComplete,
  featured = false,
}) {
  const [done, setDone] = useState(completed);
  const [animating, setAnimating] = useState(false);
  const meta = categoryMeta[category] || categoryMeta['Personnel'];

  const handleComplete = () => {
    if (done) return;
    setAnimating(true);
    setTimeout(() => {
      setDone(true);
      setAnimating(false);
      if (onComplete) onComplete();
    }, 600);
  };

  return (
    <div className={`mission-card${featured ? ' mission-card--featured' : ''}${done ? ' mission-card--done' : ''}`}>
      {featured && (
        <div className="mission-card__featured-badge">
          ⚡ Défi du jour
        </div>
      )}

      <div className="mission-card__top">
        <div className={`mission-card__category mission-card__category--${meta.color}`}>
          <span>{meta.icon}</span>
          <span>{meta.label}</span>
        </div>
        <div className="mission-card__points">
          <span className="mission-card__points-icon">💧</span>
          <span className="mission-card__points-val">+{points} pts</span>
        </div>
      </div>

      <div className="mission-card__body">
        <h3 className="mission-card__title">{title}</h3>
        <p className="mission-card__desc">{description}</p>
      </div>

      <div className="mission-card__meta">
        <span className="mission-card__meta-item">
          <span>⏱</span> {duration}
        </span>
        <span className="mission-card__meta-sep">·</span>
        <span className={`mission-card__meta-diff mission-card__meta-diff--${difficulty.toLowerCase()}`}>
          {difficulty === 'Facile'  ? '🟢' : difficulty === 'Moyen' ? '🟡' : '🔴'} {difficulty}
        </span>
      </div>

      <button
        className={`mission-card__btn${done ? ' mission-card__btn--done' : ''}${animating ? ' mission-card__btn--animating' : ''}`}
        onClick={handleComplete}
        disabled={done}
      >
        {done ? (
          <>✅ Mission accomplie !</>
        ) : animating ? (
          <>⏳ Validation...</>
        ) : (
          <>🎯 Mission accomplie</>
        )}
      </button>
    </div>
  );
}
