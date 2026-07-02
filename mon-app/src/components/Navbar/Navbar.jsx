import { useState, useEffect } from 'react';
import './Navbar.css';

const navLinks = [
  { label: 'Accueil', href: '#accueil', icon: '🏠' },
  { label: 'Missions', href: '#missions', icon: '🎯' },
  { label: 'Badges', href: '#badges', icon: '🏅' },
  { label: 'Profil', href: '#profil', icon: '👤' },
];

export default function Navbar({ activePage, onNavigate }) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleNav = (href, label) => {
    setMenuOpen(false);
    if (onNavigate) onNavigate(label);
  };

  return (
    <nav className={`navbar${scrolled ? ' navbar--scrolled' : ''}`}>
      <div className="navbar__inner">
        {/* Logo */}
        <a className="navbar__logo" href="#accueil" onClick={() => handleNav('#accueil', 'Accueil')}>
          <span className="navbar__logo-drop">💧</span>
          <span className="navbar__logo-text">
            Mission <span className="navbar__logo-accent">Goutte à Goutte</span>
          </span>
        </a>

        {/* Desktop Nav */}
        <ul className="navbar__links">
          {navLinks.map(link => (
            <li key={link.label}>
              <a
                href={link.href}
                className={`navbar__link${activePage === link.label ? ' navbar__link--active' : ''}`}
                onClick={() => handleNav(link.href, link.label)}
              >
                <span className="navbar__link-icon">{link.icon}</span>
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <button className="navbar__cta" onClick={() => handleNav('#missions', 'Missions')}>
          <span>Mes missions</span>
          <span className="navbar__cta-arrow">→</span>
        </button>

        {/* Burger */}
        <button
          className={`navbar__burger${menuOpen ? ' navbar__burger--open' : ''}`}
          onClick={() => setMenuOpen(v => !v)}
          aria-label="Menu"
        >
          <span /><span /><span />
        </button>
      </div>

      {/* Mobile Menu */}
      <div className={`navbar__mobile${menuOpen ? ' navbar__mobile--open' : ''}`}>
        <ul className="navbar__mobile-links">
          {navLinks.map(link => (
            <li key={link.label}>
              <a
                href={link.href}
                className={`navbar__mobile-link${activePage === link.label ? ' navbar__mobile-link--active' : ''}`}
                onClick={() => handleNav(link.href, link.label)}
              >
                <span className="navbar__mobile-icon">{link.icon}</span>
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
