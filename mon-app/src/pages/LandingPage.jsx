import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import "./LandingPage.css";

import heroFiltrationImage from "../assets/hero-filtration-eau.png";
import heroNettoyageImage from "../assets/hero-nettoyage-cours-eau.png";
import heroRecuperationImage from "../assets/hero-recuperation-eau-pluie.png";
import heroEconomieImage from "../assets/hero-economie-eau.png";
import heroReparationImage from "../assets/hero-reparation-fuite.png";
import categoryProtegerSourcesImage from "../assets/categorie-proteger-sources.png";
import categoryReutiliserImage from "../assets/categorie-reutiliser-eau.png";
import categoryNettoyerImage from "../assets/categorie-nettoyer-nature.png";
import categorySensibiliserImage from "../assets/categorie-sensibiliser.png";
import categoryAmbassadeurImage from "../assets/categorie-ambassadeur-eau.png";

function LandingPage({ onNavigate = () => {} }) {
  const [language, setLanguage] = useState("FR");
  const [wordIndex, setWordIndex] = useState(0);
  const [activeSection, setActiveSection] = useState("home");

  const content = {
    FR: {
      nav: {
        home: "Accueil",
        about: "Projet",
        challenges: "Challenges",
        community: "Communauté",
        signup: "S'inscrire",
        login: "Se connecter",
      },
      hero: {
        titleStart: "Relève les plus beaux défis pour",
        rotatingWords: [
          "protéger l’eau",
          "économiser l’eau",
          "préserver l’eau",
          "valoriser l’eau",
        ],
        description:
          "Participe à des challenges simples et concrets pour apprendre à économiser l’eau, sensibiliser ton entourage et devenir Ambassadrice ou Ambassadeur de l’Eau.",
      },
      playCard: {
        levelLabel: "Niveau",
        levelValue: "Débutant",
        categoryLabel: "Catégorie",
        categoryValue: "Économie d’eau",
        profileLabel: "Profil",
        profileValue: "Guide",
        button: "Jouer",
      },
      categoriesTitle: "Catégories",
      categoriesDesc:
        "Découvre les différents types de challenges pour apprendre à économiser, protéger et valoriser l’eau.",
      challengesTitle: "Challenges populaires",
      challengesDesc:
        "Des défis simples, progressifs et adaptés au contexte de Madagascar.",
      reviewTitle: "Témoignages",
      reviewDesc:
        "Les jeunes deviennent acteurs du changement dans leur communauté.",
      reviewText:
        "Grâce à Water Challenge, j’ai appris que les petits gestes peuvent avoir un grand impact. J’ai sensibilisé ma famille et mon groupe à mieux utiliser l’eau chaque jour.",
      reviewName: "Jeune participante",
      reviewRole: "Future Ambassadrice de l’Eau",
      contactLabel: "Nous contacter",
      contactTitle: "Tu veux rejoindre ou soutenir Water Challenge ?",
      contactText:
        "Contacte l’équipe du projet pour participer, proposer un partenariat ou organiser des challenges dans ton école, ton groupe ou ta communauté.",
      footerText:
        "Une initiative inspirée du Helen Storrow Seminar 2026 pour encourager la conservation de l’eau à Madagascar.",
      footerGoal:
        "Former des jeunes capables d’agir, sensibiliser et devenir Ambassadrices ou Ambassadeurs de l’Eau.",
    },

    MLG: {
      nav: {
        home: "Fandraisana",
        about: "Tetikasa",
        challenges: "Fanamby",
        community: "Vondrona",
        signup: "Hisoratra",
        login: "Hiditra",
      },
      hero: {
        titleStart: "Ataovy ireo fanamby mba",
        rotatingWords: [
          "hiarovana ny rano",
          "hitsitsiana rano",
          "hikajiana ny rano",
          // "hanomezan-danja ny rano",
        ],
        description:
          "Mandraisa anjara amin’ny fanamby tsotra sy azo tanterahina mba hianarana mitsitsy rano, hanentanana ny manodidina ary ho Ambasadaoro mpiaro ny Rano.",
      },
      playCard: {
        levelLabel: "Ambaratonga",
        levelValue: "Mpianatra",
        categoryLabel: "Sokajy",
        categoryValue: "Fitsitsiana rano",
        profileLabel: "Mombamomba",
        profileValue: "Guide",
        button: "Hilalao",
      },
      categoriesTitle: "Sokajy",
      categoriesDesc:
        "Fantaro ireo karazana fanamby hianarana mitsitsy, miaro ary manome lanja ny rano.",
      challengesTitle: "Fanamby malaza",
      challengesDesc:
        "Fanamby tsotra, miandalana ary mifanaraka amin’ny zava-misy eto Madagasikara.",
      reviewTitle: "Fijoroana vavolombelona",
      reviewDesc:
        "Lasa mpitarika fiovana eo amin’ny fiarahamonina ny tanora.",
      reviewText:
        "Noho ny Water Challenge dia nianatra aho fa mety hitondra vokatra lehibe ny fihetsika kely. Nampianatra ny fianakaviako sy ny vondrona misy ahy aho mba hampiasa rano amim-pitandremana.",
      reviewName: "Mpandray anjara tanora",
      reviewRole: "Ho Ambasadaoro mpiaro ny Rano",
      contactLabel: "Hifandray aminay",
      contactTitle: "Te hiditra na hanohana ny Water Challenge ve ianao ?",
      contactText:
        "Mifandraisa amin’ny ekipan’ny tetikasa raha te handray anjara, hanao fiaraha-miasa na hikarakara fanamby ao amin’ny sekoly, vondrona na fiarahamonina misy anao.",
      footerText:
        "Tetikasa avy amin’ny Helen Storrow Seminar 2026 hanentanana ny fiarovana sy fitsitsiana rano eto Madagasikara.",
      footerGoal:
        "Manofana tanora afaka mihetsika, manentana ary ho Ambasadaoro mpiaro ny Rano.",
    },
  };

  const t = content[language];

  const menuItems = useMemo(
    () => [
      { id: "home", label: "home" },
      { id: "categories", label: "about" },
      { id: "challenges", label: "challenges" },
      { id: "review", label: "community" },
    ],
    []
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setWordIndex((current) => (current + 1) % t.hero.rotatingWords.length);
    }, 2600);

    return () => clearInterval(interval);
  }, [language, t.hero.rotatingWords.length]);

  useEffect(() => {
    const handleScroll = () => {
      const sectionIds = ["home", "categories", "challenges", "review", "contact"];
      const marker = 138;

      const currentSection =
        sectionIds.find((sectionId) => {
          const element = document.getElementById(sectionId);
          if (!element) return false;

          const rect = element.getBoundingClientRect();
          return rect.top <= marker && rect.bottom >= marker;
        }) || "home";

      setActiveSection(currentSection === "contact" ? "review" : currentSection);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const categories =
    language === "FR"
      ? [
          {
            title: "Économiser l’eau",
            img: heroEconomieImage,
          },
          {
            title: "Protéger les sources",
            img: categoryProtegerSourcesImage,
          },
          {
            title: "Réutiliser l’eau",
            img: categoryReutiliserImage,
          },
          {
            title: "Nettoyer la nature",
            img: categoryNettoyerImage,
          },
          {
            title: "Sensibiliser",
            img: categorySensibiliserImage,
          },
          {
            title: "Ambassadeur de l’Eau",
            img: categoryAmbassadeurImage,
          },
        ]
      : [
          {
            title: "Mitsitsy rano",
            img: heroEconomieImage,
          },
          {
            title: "Miaro loharano",
            img: categoryProtegerSourcesImage,
          },
          {
            title: "Mampiasa indray",
            img: categoryReutiliserImage,
          },
          {
            title: "Manadio tontolo",
            img: categoryNettoyerImage,
          },
          {
            title: "Manentana",
            img: categorySensibiliserImage,
          },
          {
            title: "Ambasadaoro rano",
            img: categoryAmbassadeurImage,
          },
        ];

  const challenges =
    language === "FR"
      ? [
          {
            title: "Chasse aux fuites",
            place: "Maison / École",
            points: 25,
            img: heroReparationImage,
          },
          {
            title: "Chaque goutte compte",
            place: "Challenge quotidien",
            points: 10,
            img: heroEconomieImage,
          },
          {
            title: "Nettoyer un point d’eau",
            place: "Action communautaire",
            points: 100,
            img: heroNettoyageImage,
          },
          {
            title: "Créer une affiche",
            place: "École / Quartier",
            points: 50,
            img: categorySensibiliserImage,
          },
        ]
      : [
          {
            title: "Mitady fivoahan-drano",
            place: "Trano / Sekoly",
            points: 25,
            img: heroReparationImage,
          },
          {
            title: "Sarobidy ny rano",
            place: "Fanamby isan’andro",
            points: 10,
            img: heroEconomieImage,
          },
          {
            title: "Manadio loharano",
            place: "Asa iombonana",
            points: 100,
            img: heroNettoyageImage,
          },
          {
            title: "Mamorona afisy",
            place: "Sekoly / Fokontany",
            points: 50,
            img: categorySensibiliserImage,
          },
        ];

  const fadeUp = {
    hidden: { opacity: 0, y: 45 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.75, ease: "easeOut" },
    },
  };

  const fadeLeft = {
    hidden: { opacity: 0, x: -45 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.75, ease: "easeOut" },
    },
  };

  const fadeRight = {
    hidden: { opacity: 0, x: 45 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.75, ease: "easeOut" },
    },
  };

  const staggerContainer = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.14,
      },
    },
  };

  const heroImagePop = {
    hidden: { opacity: 0, scale: 0.82, y: 35 },
    visible: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: { duration: 0.68, ease: "easeOut" },
    },
  };

  const scrollToContact = () => {
    document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <main className="wc-page">
      <motion.header
        className="wc-navbar"
        initial={{ opacity: 0, y: -25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.65, ease: "easeOut" }}
      >
        <div className="wc-logo">
          <span className="wc-logo-mark">W</span>
          <span>Water Challenge</span>
        </div>

        <nav className="wc-menu" aria-label="Navigation principale">
          {menuItems.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={activeSection === item.id ? "active" : ""}
            >
              {t.nav[item.label]}
            </a>
          ))}
        </nav>

        <div className="wc-nav-actions">
          <div className="wc-language" aria-label="Changer de langue">
            <button
              type="button"
              className={language === "FR" ? "active" : ""}
              onClick={() => {
                setLanguage("FR");
                setWordIndex(0);
              }}
            >
              FR
            </button>

            <button
              type="button"
              className={language === "MLG" ? "active" : ""}
              onClick={() => {
                setLanguage("MLG");
                setWordIndex(0);
              }}
            >
              MLG
            </button>
          </div>

          {/* <button className="wc-login-btn" type="button" onClick={() => onNavigate('login')}>
            {t.nav.login}
          </button> */}

          <button className="wc-sign-btn" type="button" onClick={() => onNavigate('signup')}>
            {t.nav.signup}
          </button>
        </div>
      </motion.header>

      <section className="wc-hero" id="home">
        <motion.div
          className="wc-hero-left"
          variants={fadeLeft}
          initial="hidden"
          animate="visible"
        >
          <h1>
            {t.hero.titleStart}{" "}
            <AnimatePresence mode="wait">
              <motion.span
                key={`${language}-${wordIndex}`}
                className="wc-changing-word"
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -18 }}
                transition={{ duration: 0.45, ease: "easeOut" }}
              >
                {t.hero.rotatingWords[wordIndex]}
              </motion.span>
            </AnimatePresence>
          </h1>

          <motion.span
            className="wc-hero-arrow"
            animate={{ rotate: [18, 28, 18], y: [0, -8, 0] }}
            transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
          >
            ↝
          </motion.span>

          <p className="wc-hero-text">{t.hero.description}</p>

          <motion.div
            className="wc-play-card"
            initial={{ opacity: 0, y: 35 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.75, delay: 0.3, ease: "easeOut" }}
          >
            <div className="wc-play-item">
              <label>{t.playCard.levelLabel}</label>
              <p>{t.playCard.levelValue}</p>
            </div>

            <div className="wc-play-item">
              <label>{t.playCard.categoryLabel}</label>
              <p>{t.playCard.categoryValue}</p>
            </div>

            <div className="wc-play-item">
              <label>{t.playCard.profileLabel}</label>
              <p>{t.playCard.profileValue}</p>
            </div>

            <button type="button" onClick={() => onNavigate('login')}>{t.playCard.button}</button>
          </motion.div>
        </motion.div>

        <motion.div
          className="wc-hero-right"
          variants={fadeRight}
          initial="hidden"
          animate="visible"
        >
          <motion.div
            className="wc-image-collage"
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
          >
            <span className="wc-dotted-box wc-dotted-one"></span>
            <span className="wc-dotted-box wc-dotted-two"></span>

            <motion.img
              variants={heroImagePop}
              className="wc-img wc-img-one"
              src={heroFiltrationImage}
              alt="Installation de filtration de l’eau"
              whileHover={{ y: -8, scale: 1.03 }}
            />

            <motion.img
              variants={heroImagePop}
              className="wc-img wc-img-two"
              src={heroNettoyageImage}
              alt="Scouts nettoyant un cours d’eau"
              whileHover={{ y: -8, scale: 1.03 }}
            />

            <motion.img
              variants={heroImagePop}
              className="wc-img wc-img-three"
              src={heroRecuperationImage}
              alt="Récupération de l’eau de pluie"
              whileHover={{ y: -8, scale: 1.03 }}
            />

            <motion.img
              variants={heroImagePop}
              className="wc-img wc-img-four"
              src={heroReparationImage}
              alt="Réparation d’une fuite d’eau"
              whileHover={{ y: -8, scale: 1.03 }}
            />

            <motion.img
              variants={heroImagePop}
              className="wc-img wc-img-five"
              src={heroEconomieImage}
              alt="Geste quotidien pour économiser l’eau"
              whileHover={{ y: -8, scale: 1.03 }}
            />

            <motion.span
              className="wc-corner-lines"
              animate={{ rotate: [24, 34, 24], scale: [1, 1.08, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
              )))
            </motion.span>
          </motion.div>
        </motion.div>
      </section>

      <motion.section
        className="wc-section wc-intro-categories"
        id="categories"
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.25 }}
      >
        <div className="wc-categories-header">
          <h2>{t.categoriesTitle}</h2>
          <p>{t.categoriesDesc}</p>
        </div>

        <motion.div
          className="wc-categories"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
        >
          {categories.map((cat, index) => (
            <motion.div
              className="wc-category"
              key={cat.title}
              variants={fadeUp}
              whileHover={{ y: -8, transition: { duration: 0.25, ease: "easeOut" } }}
            >
              <motion.div
                className="wc-category-image-wrap"
                whileHover={{ scale: 1.04 }}
                transition={{ duration: 0.25 }}
              >
                <img src={cat.img} alt={cat.title} loading={index > 1 ? "lazy" : "eager"} />
              </motion.div>

              <p>{cat.title}</p>
            </motion.div>
          ))}
        </motion.div>
      </motion.section>

      <motion.section
        className="wc-section"
        id="challenges"
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
      >
        <div className="wc-section-title-row">
          <div>
            <h2>{t.challengesTitle}</h2>
            <p>{t.challengesDesc}</p>
          </div>

          <div className="wc-slider-buttons">
            <button type="button" aria-label="Challenge précédent">←</button>
            <button type="button" aria-label="Challenge suivant">→</button>
          </div>
        </div>

        <motion.div
          className="wc-challenge-list"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
        >
          {challenges.map((challenge) => (
            <motion.article
              className="wc-challenge-card"
              key={challenge.title}
              variants={fadeUp}
              whileHover={{ y: -8 }}
            >
              <img src={challenge.img} alt={challenge.title} loading="lazy" />

              <div className="wc-card-content">
                <p>{challenge.place}</p>
                <h3>{challenge.title}</h3>

                <div className="wc-card-bottom">
                  <strong>{challenge.points} pts</strong>
                  <button type="button">
                    {language === "FR" ? "Voir plus" : "Hijery"}
                  </button>
                </div>
              </div>
            </motion.article>
          ))}
        </motion.div>
      </motion.section>

      <motion.section
        className="wc-book-section"
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
      >
        <motion.div className="wc-step-card" whileHover={{ y: -5 }}>
          <div className="wc-mini-card active">
            <span>01</span>

            <div>
              <h3>{language === "FR" ? "Choisir un challenge" : "Misafidy fanamby"}</h3>
              <p>
                {language === "FR"
                  ? "L’utilisateur choisit un défi selon son niveau et sa catégorie."
                  : "Misafidy fanamby mifanaraka amin’ny ambaratonga sy sokajy ny mpampiasa."}
              </p>
            </div>
          </div>

          <div className="wc-mini-card">
            <span>02</span>

            <div>
              <h3>{language === "FR" ? "Réaliser l’action" : "Manatanteraka asa"}</h3>
              <p>
                {language === "FR"
                  ? "Il applique le geste dans sa maison, son école ou sa communauté."
                  : "Ataony ao an-trano, sekoly na fiarahamonina ny asa."}
              </p>
            </div>
          </div>

          <div className="wc-mini-card">
            <span>03</span>

            <div>
              <h3>{language === "FR" ? "Envoyer une preuve" : "Mandefa porofo"}</h3>
              <p>
                {language === "FR"
                  ? "Il soumet une photo, un texte ou une vidéo courte pour validation."
                  : "Mandefa sary, lahatsoratra na vidéo fohy hohamarinina."}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div className="wc-action-image" whileHover={{ scale: 1.015 }}>
          <img
            src={heroNettoyageImage}
            alt="Scouts participant au nettoyage d’un cours d’eau"
            loading="lazy"
          />
        </motion.div>
      </motion.section>

      <motion.section
        className="wc-section wc-review"
        id="review"
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
      >
        <div className="wc-section-title-row">
          <div>
            <h2>{t.reviewTitle}</h2>
            <p>{t.reviewDesc}</p>
          </div>

          <div className="wc-slider-buttons">
            <button type="button" aria-label="Témoignage précédent">←</button>
            <button type="button" aria-label="Témoignage suivant">→</button>
          </div>
        </div>

        <div className="wc-review-content">
          <motion.div className="wc-review-img-box" whileHover={{ y: -8 }}>
            <img
              src={categoryAmbassadeurImage}
              alt="Jeune ambassadrice de l’eau"
              loading="lazy"
            />

            <span className="wc-review-shape"></span>
          </motion.div>

          <motion.div className="wc-review-card" whileHover={{ y: -5 }}>
            <div className="wc-quote">“</div>

            <p>{t.reviewText}</p>

            <h4>{t.reviewName}</h4>
            <span>{t.reviewRole}</span>
          </motion.div>
        </div>
      </motion.section>

      <motion.section
        className="wc-contact-section"
        id="contact"
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
      >
        <div className="wc-contact-left">
          <p className="wc-small-label">{t.contactLabel}</p>
          <h2>{t.contactTitle}</h2>
          <p>{t.contactText}</p>

          <div className="wc-contact-info">
            <div>
              <strong>Email</strong>
              <span>waterchallenge@faniloni-madagascar.org</span>
            </div>

            <div>
              <strong>Projet</strong>
              <span>Fanilon’i Madagascar • Conservation de l’eau</span>
            </div>
          </div>
        </div>

        <form className="wc-contact-form">
          <input type="text" placeholder={language === "FR" ? "Votre nom" : "Anaranao"} />

          <input type="email" placeholder={language === "FR" ? "Votre email" : "Email-nao"} />

          <select defaultValue="">
            <option value="" disabled>
              {language === "FR" ? "Vous êtes..." : "Ianao dia..."}
            </option>
            <option>Guide</option>
            <option>{language === "FR" ? "Non-guide" : "Tsy guide"}</option>
            <option>{language === "FR" ? "École / Association" : "Sekoly / Fikambanana"}</option>
            <option>Partenaire</option>
          </select>

          <textarea placeholder={language === "FR" ? "Votre message" : "Hafatrao"}></textarea>

          <button type="button">
            {language === "FR" ? "Envoyer le message" : "Alefa ny hafatra"}
          </button>
        </form>
      </motion.section>

      <footer className="wc-footer">
        <div>
          <h3>Water Challenge</h3>
          <p>{t.footerText}</p>
        </div>

        <div>
          <h4>Navigation</h4>
          <a href="#home">{t.nav.home}</a>
          <a href="#categories">{t.nav.about}</a>
          <a href="#challenges">{t.nav.challenges}</a>
          <a href="#review">{t.nav.community}</a>
          <a href="#contact">Contact</a>
        </div>

        <div>
          <h4>Objectif</h4>
          <p>{t.footerGoal}</p>
        </div>
      </footer>

      <div className="wc-copyright">
        © 2026 Water Challenge — Fanilon’i Madagascar. Tous droits réservés.
      </div>
    </main>
  );
}

export default LandingPage;