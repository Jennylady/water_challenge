import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer__wave" aria-hidden="true">
        <svg viewBox="0 0 1200 80" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
          <path d="M0,40 C200,80 400,0 600,40 C800,80 1000,0 1200,40 L1200,80 L0,80 Z" fill="#1a3496" />
        </svg>
      </div>

      <div className="footer__inner">
        <div className="footer__main">
          {/* Brand */}
          <div className="footer__brand">
            <div className="footer__logo">
              <span className="footer__logo-drop">💧</span>
              <span className="footer__logo-text">Mission Goutte à Goutte</span>
            </div>
            <p className="footer__tagline">
              Chaque goutte compte, chaque scout agit.
            </p>
            <div className="footer__social">
              <a href="#" className="footer__social-btn" aria-label="Instagram">📸</a>
              <a href="#" className="footer__social-btn" aria-label="Twitter">🐦</a>
              <a href="#" className="footer__social-btn" aria-label="YouTube">▶️</a>
            </div>
          </div>

          {/* Links */}
          <div className="footer__col">
            <h4 className="footer__col-title">Navigation</h4>
            <ul className="footer__col-links">
              <li><a href="#accueil">🏠 Accueil</a></li>
              <li><a href="#missions">🎯 Missions</a></li>
              <li><a href="#badges">🏅 Badges</a></li>
              <li><a href="#profil">👤 Profil</a></li>
            </ul>
          </div>

          <div className="footer__col">
            <h4 className="footer__col-title">À propos</h4>
            <ul className="footer__col-links">
              <li><a href="#">🌊 Notre mission</a></li>
              <li><a href="#">👥 La patrouille</a></li>
              <li><a href="#">📚 Ressources</a></li>
              <li><a href="#">📬 Contact</a></li>
            </ul>
          </div>

          <div className="footer__col">
            <h4 className="footer__col-title">Rejoindre</h4>
            <p className="footer__newsletter-text">
              Reçois les défis de la semaine !
            </p>
            <div className="footer__newsletter">
              <input
                type="email"
                placeholder="Ton email"
                className="footer__newsletter-input"
              />
              <button className="footer__newsletter-btn">→</button>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="footer__bottom">
          <span>💧 Mission Goutte à Goutte © 2026</span>
          <span className="footer__bottom-sep">·</span>
          <span>Fait avec 💙 pour les scouts</span>
          <span className="footer__bottom-sep">·</span>
          <a href="#">Mentions légales</a>
        </div>
      </div>
    </footer>
  );
}
