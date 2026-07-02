import './Hero.css';

export default function Hero({ onNavigate }) {
  return (
    <section className="hero" id="accueil">
      {/* Animated water background */}
      <div className="hero__waves">
        <div className="hero__wave hero__wave--1" />
        <div className="hero__wave hero__wave--2" />
      </div>

      {/* Floating drops deco */}
      <div className="hero__drops" aria-hidden="true">
        <span className="hero__drop hero__drop--1">💧</span>
        <span className="hero__drop hero__drop--2">💧</span>
        <span className="hero__drop hero__drop--3">🌊</span>
        <span className="hero__drop hero__drop--4">💧</span>
        <span className="hero__drop hero__drop--5">⚜️</span>
      </div>

      <div className="hero__inner">
        {/* Left: Text */}
        <div className="hero__content">
          <div className="hero__badge-pill">
            <span className="hero__badge-dot" />
            <span>🌍 Scouts pour la planète</span>
          </div>

          <h1 className="hero__title">
            Mission<br />
            <span className="hero__title-highlight">Goutte à Goutte</span>
          </h1>

          <p className="hero__subtitle">
            Chaque goutte compte,<br />
            <strong>chaque scout agit.</strong>
          </p>

          <p className="hero__desc">
            Rejoins la brigade de l'eau, accomplis des défis, gagne des badges et 
            deviens le gardien de notre ressource la plus précieuse.
          </p>

          <div className="hero__actions">
            <button
              className="hero__btn hero__btn--primary"
              onClick={() => onNavigate && onNavigate('Missions')}
            >
              <span>🚀 Commencer</span>
            </button>
            <button
              className="hero__btn hero__btn--secondary"
              onClick={() => onNavigate && onNavigate('Missions')}
            >
              <span>🎯 Voir mes missions</span>
            </button>
          </div>

          {/* Stats strip */}
          <div className="hero__stats">
            <div className="hero__stat">
              <span className="hero__stat-num">2 450</span>
              <span className="hero__stat-label">Scouts actifs</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">18 200</span>
              <span className="hero__stat-label">Missions</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">340 kL</span>
              <span className="hero__stat-label">Eau préservée</span>
            </div>
          </div>
        </div>

        {/* Right: Illustration */}
        <div className="hero__illustration">
          <div className="hero__illus-ring hero__illus-ring--outer" />
          <div className="hero__illus-ring hero__illus-ring--mid" />
          <div className="hero__illus-card">
            <div className="hero__illus-icon">💧</div>
            <div className="hero__illus-planet">
              <div className="hero__illus-earth">🌍</div>
              <div className="hero__illus-orbit">
                <div className="hero__illus-orbiting">⚜️</div>
              </div>
            </div>
            <div className="hero__illus-label">Protège la planète</div>
            <div className="hero__illus-sub">Mission active</div>
            <div className="hero__illus-progress">
              <div className="hero__illus-bar">
                <div className="hero__illus-fill" />
              </div>
              <span>72% accomplie</span>
            </div>
          </div>

          {/* Floating mini-cards */}
          <div className="hero__mini-card hero__mini-card--top">
            <span>🏅</span>
            <div>
              <p className="hero__mini-title">Nouveau badge !</p>
              <p className="hero__mini-sub">Gardien de la source</p>
            </div>
          </div>
          <div className="hero__mini-card hero__mini-card--bot">
            <span>🔥</span>
            <div>
              <p className="hero__mini-title">Série : 7 jours</p>
              <p className="hero__mini-sub">Continue comme ça !</p>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll hint */}
      <div className="hero__scroll-hint">
        <div className="hero__scroll-dot" />
        <span>Découvre plus</span>
      </div>
    </section>
  );
}
