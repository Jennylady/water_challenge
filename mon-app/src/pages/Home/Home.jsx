import Hero from '../../components/Hero/Hero';
import Dashboard from '../../components/Dashboard/Dashboard';
import MissionCard from '../../components/MissionCard/MissionCard';
import ProgressSection from '../../components/ProgressSection/ProgressSection';
import HistorySection from '../../components/HistorySection/HistorySection';
import './Home.css';

const dailyMission = {
  title: 'Parle à un ami d\'une économie d\'eau',
  category: 'Sensibilisation',
  description:
    'Explique à un camarade ou un membre de ta famille une astuce simple pour économiser l\'eau au quotidien. Chaque conversation compte !',
  points: 80,
  difficulty: 'Facile',
  duration: '10 min',
  featured: true,
};

const missions = [
  {
    id: 1,
    title: 'Ferme le robinet pendant le brossage',
    category: 'Personnel',
    description: 'Garde le robinet fermé pendant que tu te brosses les dents. Tu économises jusqu\'à 12 litres d\'eau !',
    points: 50,
    difficulty: 'Facile',
    duration: '3 min',
  },
  {
    id: 2,
    title: 'Collecte d\'eau de pluie',
    category: 'Terrain',
    description: 'Installe un récupérateur d\'eau de pluie ou aide ton équipe à en installer un dans un espace vert.',
    points: 120,
    difficulty: 'Moyen',
    duration: '45 min',
  },
  {
    id: 3,
    title: 'Répare une fuite d\'eau',
    category: 'Personnel',
    description: 'Repère et signale (ou répare) une fuite chez toi ou dans ta structure scoute. Chaque goutte perdue compte.',
    points: 100,
    difficulty: 'Moyen',
    duration: '20 min',
  },
  {
    id: 4,
    title: 'Organise un atelier eau',
    category: 'Sensibilisation',
    description: 'Monte un atelier de 10 minutes avec ta patrouille sur le cycle de l\'eau ou la pollution des rivières.',
    points: 200,
    difficulty: 'Difficile',
    duration: '1h',
  },
  {
    id: 5,
    title: 'Nettoyage d\'un cours d\'eau',
    category: 'Terrain',
    description: 'Participe à une action de nettoyage d\'une rivière, d\'un lac ou d\'une mare près de chez toi.',
    points: 250,
    difficulty: 'Difficile',
    duration: '2h',
  },
];

export default function Home({ onNavigate }) {
  return (
    <div className="home page-enter">
      <Hero onNavigate={onNavigate} />
      <Dashboard />

      {/* Daily challenge */}
      <section className="home__daily" id="defi">
        <div className="home__daily-inner">
          <div className="home__daily-header">
            <div>
              <h2 className="home__section-title">⚡ Défi du jour</h2>
              <p className="home__section-sub">Un nouveau défi chaque jour pour agir concrètement.</p>
            </div>
            <div className="home__daily-countdown">
              <span className="home__daily-countdown-icon">⏰</span>
              <div>
                <div className="home__daily-countdown-val">14:32:10</div>
                <div className="home__daily-countdown-label">Expire dans</div>
              </div>
            </div>
          </div>
          <div className="home__daily-card">
            <MissionCard {...dailyMission} />
          </div>
        </div>
      </section>

      {/* All missions */}
      <section className="home__missions" id="missions">
        <div className="home__missions-inner">
          <div className="home__missions-header">
            <div>
              <h2 className="home__section-title">🎯 Toutes les missions</h2>
              <p className="home__section-sub">Explore et accomplis les missions à ton rythme.</p>
            </div>
            <div className="home__missions-filters">
              <button className="home__filter-btn home__filter-btn--active">Toutes</button>
              <button className="home__filter-btn">🪥 Personnel</button>
              <button className="home__filter-btn">📢 Sensibilisation</button>
              <button className="home__filter-btn">🌿 Terrain</button>
            </div>
          </div>
          <div className="home__missions-grid">
            {missions.map((m, i) => (
              <div key={m.id} style={{ animationDelay: `${i * 0.08}s` }}>
                <MissionCard {...m} />
              </div>
            ))}
          </div>
        </div>
      </section>

      <ProgressSection />
      <HistorySection />
    </div>
  );
}
