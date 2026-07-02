import { useState } from 'react';
import MissionCard from '../../components/MissionCard/MissionCard';
import './Missions.css';

const allMissions = [
  { id: 1,  title: 'Ferme le robinet pendant le brossage', category: 'Personnel',       description: 'Garde le robinet fermé pendant que tu te brosses les dents. Tu économises jusqu\'à 12 litres d\'eau !', points: 50,  difficulty: 'Facile',   duration: '3 min' },
  { id: 2,  title: 'Parle à un ami d\'une économie d\'eau', category: 'Sensibilisation', description: 'Explique une astuce simple pour économiser l\'eau à un camarade ou un membre de ta famille.', points: 80,  difficulty: 'Facile',   duration: '10 min' },
  { id: 3,  title: 'Collecte d\'eau de pluie',              category: 'Terrain',         description: 'Installe un récupérateur d\'eau de pluie ou aide ton équipe à en installer un.', points: 120, difficulty: 'Moyen',    duration: '45 min' },
  { id: 4,  title: 'Répare une fuite d\'eau',               category: 'Personnel',       description: 'Repère et signale (ou répare) une fuite chez toi ou dans ta structure scoute.', points: 100, difficulty: 'Moyen',    duration: '20 min' },
  { id: 5,  title: 'Organise un atelier eau',               category: 'Sensibilisation', description: 'Monte un atelier de 10 minutes avec ta patrouille sur le cycle de l\'eau.', points: 200, difficulty: 'Difficile', duration: '1h' },
  { id: 6,  title: 'Nettoyage d\'un cours d\'eau',          category: 'Terrain',         description: 'Participe à une action de nettoyage d\'une rivière, d\'un lac ou d\'une mare.', points: 250, difficulty: 'Difficile', duration: '2h' },
  { id: 7,  title: 'Douche de 5 minutes chronométrée',      category: 'Personnel',       description: 'Chronomètre ta douche et vise moins de 5 minutes. Défi à faire 7 jours d\'affilée !', points: 60,  difficulty: 'Facile',   duration: '5 min' },
  { id: 8,  title: 'Crée une affiche de sensibilisation',   category: 'Sensibilisation', description: 'Réalise une affiche créative sur l\'économie d\'eau et colle-la dans ton école ou centre.', points: 110, difficulty: 'Moyen',    duration: '30 min' },
  { id: 9,  title: 'Analyse de la qualité d\'eau',          category: 'Terrain',         description: 'Effectue un test simple de qualité d\'eau d\'un ruisseau local et note tes observations.', points: 180, difficulty: 'Difficile', duration: '1h30' },
];

const categories = ['Toutes', 'Personnel', 'Sensibilisation', 'Terrain'];
const catIcons = { Personnel: '🪥', Sensibilisation: '📢', Terrain: '🌿', Toutes: '⚡' };

export default function Missions() {
  const [activeCategory, setActiveCategory] = useState('Toutes');
  const [completedIds, setCompletedIds] = useState(new Set());

  const filtered = activeCategory === 'Toutes'
    ? allMissions
    : allMissions.filter(m => m.category === activeCategory);

  const handleComplete = (id) => {
    setCompletedIds(prev => new Set([...prev, id]));
  };

  return (
    <div className="missions-page page-enter">
      {/* Hero banner */}
      <div className="missions-page__hero">
        <div className="missions-page__hero-inner">
          <h1 className="missions-page__hero-title">🎯 Mes Missions</h1>
          <p className="missions-page__hero-sub">
            Accomplis des défis, gagne des points et protège notre planète.
          </p>
          <div className="missions-page__hero-stats">
            <div className="missions-page__hero-stat">
              <span className="missions-page__hero-stat-val">{completedIds.size}</span>
              <span className="missions-page__hero-stat-label">Accomplies</span>
            </div>
            <div className="missions-page__hero-stat-div" />
            <div className="missions-page__hero-stat">
              <span className="missions-page__hero-stat-val">{allMissions.length - completedIds.size}</span>
              <span className="missions-page__hero-stat-label">Restantes</span>
            </div>
            <div className="missions-page__hero-stat-div" />
            <div className="missions-page__hero-stat">
              <span className="missions-page__hero-stat-val">
                {allMissions.filter(m => completedIds.has(m.id)).reduce((s, m) => s + m.points, 0)}
              </span>
              <span className="missions-page__hero-stat-label">Pts gagnés</span>
            </div>
          </div>
        </div>
      </div>

      {/* Filters + grid */}
      <div className="missions-page__content">
        <div className="missions-page__content-inner">
          <div className="missions-page__filters">
            {categories.map(cat => (
              <button
                key={cat}
                className={`missions-page__filter${activeCategory === cat ? ' missions-page__filter--active' : ''}`}
                onClick={() => setActiveCategory(cat)}
              >
                <span>{catIcons[cat]}</span>
                <span>{cat}</span>
                <span className="missions-page__filter-count">
                  {cat === 'Toutes' ? allMissions.length : allMissions.filter(m => m.category === cat).length}
                </span>
              </button>
            ))}
          </div>

          <div className="missions-page__grid">
            {filtered.map((m, i) => (
              <div key={m.id} style={{ animationDelay: `${i * 0.07}s` }}>
                <MissionCard
                  {...m}
                  completed={completedIds.has(m.id)}
                  onComplete={() => handleComplete(m.id)}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
