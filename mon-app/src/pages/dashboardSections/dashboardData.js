export function getDashboardData(language = 'FR') {
  const FR = {
    logout: 'Déconnexion',
    waterAmbassador: 'Ambassadeur de l’eau',
    levelBeginner: 'Débutant',
    firstBadge: 'Éco-Geste',
    menu: {
      dashboard: 'Tableau de bord',
      learning: 'Formation',
      challenges: 'Défis',
      submit: 'Soumission',
      activities: 'Mes activités',
      projects: 'Projets',
      community: 'Communauté',
      badges: 'Insignes et certificats',
      profile: 'Profil',
    },
    home: {
      kicker: 'Espace ambassadeur',
      title: 'Bienvenue dans Water Challenge',
      subtitle: 'Apprends, réalise des défis simples, envoie tes preuves et deviens Ambassadeur de l’Eau dans ta communauté.',
      progression: 'Progression',
      points: 'Points',
      level: 'Niveau',
      badges: 'Insignes',
      pending: 'En attente',
      peopleTouched: 'Personnes touchées',
      continueLearning: 'Continuer la formation',
      submitProof: 'Envoyer une activité',
      notificationsTitle: 'Notifications',
      ongoingTitle: 'Défis en cours',
    },
    learning: {
      
      title: 'Modules de formation',
      subtitle: 'Chaque module suit un parcours simple : petite explication, lecture, quiz, challenge, puis soumission de preuve.',
      read: 'Lire',
      quiz: 'Quiz',
      challenge: 'Défi',
      submit: 'Soumettre',
      start: 'Commencer',
    },
    challenges: {
      kicker: 'Actions concrètes',
      title: 'Tous les défis',
      subtitle: 'Choisis un défi, lis l’objectif et les instructions, puis réalise l’activité dans ta maison, ton école ou ta communauté.',
      objective: 'Objectif',
      difficulty: 'Difficulté',
      points: 'Points',
      duration: 'Durée',
      instructions: 'Instructions',
      submit: 'Soumettre ce challenge',
    },
    submit: {
      kicker: 'Preuve d’activité',
      title: 'Soumettre une activité',
      subtitle: 'Envoie une preuve claire de ton action : photo, texte, date, lieu et nombre de personnes touchées.',
      challenge: 'Défi',
      titleLabel: 'Titre de l’activité',
      date: 'Date',
      place: 'Lieu',
      people: 'Nombre de personnes touchées',
      photo: 'Photo',
      video: 'Vidéo optionnelle',
      description: 'Description / preuve texte',
      submitButton: 'Envoyer l’activité',
      saved: 'Activité enregistrée localement et mise en attente de validation.',
      fileNote: 'Prototype local : seuls les noms des fichiers sont sauvegardés, pas les fichiers eux-mêmes.',
    },
    activities: {
      kicker: 'Historique',
      title: 'Mes activités',
      subtitle: 'Retrouve tes activités envoyées : en attente, validées, refusées ou à corriger.',
      empty: 'Aucune activité envoyée pour le moment.',
      pending: 'En attente',
      validated: 'Validé',
      rejected: 'Refusé',
      toCorrect: 'À corriger',
    },
    projects: {
      kicker: 'Impact local',
      title: 'Projets communautaires',
      subtitle: 'Crée et suis tes projets communautaires autour de l’eau : sensibilisation, nettoyage, protection de sources ou campagne locale.',
      name: 'Nom du projet',
      objective: 'Objectif',
      description: 'Description',
      date: 'Date',
      place: 'Lieu',
      progress: 'Progression (%)',
      photos: 'Photos / liens',
      create: 'Créer le projet',
      existing: 'Projets créés',
      empty: 'Aucun projet communautaire créé.',
    },
    community: {
      kicker: 'Partage',
      title: 'Communauté',
      subtitle: 'Partage tes expériences, pose des questions et découvre les réalisations des autres ambassadeurs.',
      publish: 'Publier',
      placeholder: 'Partage ton expérience, une question ou une réalisation...',
    },
    badges: {
      kicker: 'Récompenses',
      title: 'Badges et certificats',
      subtitle: 'Les badges montrent ta progression. Les certificats peuvent être générés après validation de plusieurs activités.',
      certificate: 'Certificat Ambassadeur de l’eau',
      certificateText: 'Disponible après 10 défis validés et un projet communautaire terminé.',
      unlocked: 'Obtenu',
      locked: 'Bloqué',
    },
    profile: {
      kicker: 'Compte',
      title: 'Profil',
      subtitle: 'Tes informations personnelles, ton organisation, ta région et tes statistiques principales.',
      personal: 'Informations personnelles',
      organization: 'Organisation',
      stats: 'Statistiques',
    },
    status: {
      pending: 'En attente',
      validated: 'Validé',
      rejected: 'Refusé',
      toCorrect: 'À corriger',
    },
  }

  const MLG = {
    ...FR,
    logout: 'Hivoaka',
    waterAmbassador: 'Ambasadaoro Rano',
    levelBeginner: 'Mpianatra',
    firstBadge: 'Eco-Geste',
    menu: {
      dashboard: 'Tabilao lehibe',
      learning: 'Fianarana',
      challenges: 'Fanamby',
      submit: 'Mandefa asa',
      activities: 'Ny asako',
      projects: 'Tetikasa',
      community: 'Vondrona',
      badges: 'Mari-pankasitrahana',
      profile: 'Mombamomba ahy',
    },
    home: {
      ...FR.home,
      kicker: 'Sehatry ny ambasadaoro',
      title: 'Tonga soa eto amin’ny Water Challenge',
      subtitle: 'Mianara, ataovy ny fanamby tsotra, alefaso ny porofo ary misondrota ho Ambasadaoro Rano eo amin’ny fiarahamoninao.',
      progression: 'Fivoarana',
      points: 'Isa',
      level: 'Ambaratonga',
      badges: 'Insignes',
      pending: 'Miandry',
      peopleTouched: 'Olona voakasika',
      continueLearning: 'Hanohy fianarana',
      submitProof: 'Handefa asa',
      notificationsTitle: 'Fampandrenesana',
      ongoingTitle: 'Fanamby mandeha',
    },
  }

  const text = language === 'MLG' ? MLG : FR

  const modules = [
    {
      id: 1,
      title: language === 'FR' ? 'Conservation de l’eau' : 'Fitsitsiana rano',
      category: language === 'FR' ? 'Économie d’eau' : 'Fitsitsiana',
      image: 'https://images.unsplash.com/photo-1508873699372-7aeab60b44ab?auto=format&fit=crop&w=700&q=80',
      explanation:
        language === 'FR'
          ? 'Comprendre pourquoi chaque goutte compte et apprendre des gestes simples à appliquer chaque jour.'
          : 'Mahafantatra ny lanjan’ny rano sy mianatra fihetsika tsotra isan’andro.',
      quiz: '5 questions',
      points: 30,
      progress: 65,
    },
    {
      id: 2,
      title: language === 'FR' ? 'Protection des sources d’eau' : 'Miaro loharano',
      category: language === 'FR' ? 'Protection' : 'Fiarovana',
      image: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=700&q=80',
      explanation:
        language === 'FR'
          ? 'Identifier les risques autour des sources et organiser une action simple de protection.'
          : 'Mamantatra ny loza manodidina ny loharano ary mikarakara asa fiarovana.',
      quiz: '4 questions',
      points: 45,
      progress: 30,
    },
    {
      id: 3,
      title: language === 'FR' ? 'Sensibilisation communautaire' : 'Fanentanana',
      category: language === 'FR' ? 'Sensibilisation' : 'Fanentanana',
      image: 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?auto=format&fit=crop&w=700&q=80',
      explanation:
        language === 'FR'
          ? 'Apprendre à expliquer clairement un message sur l’eau à sa famille, son école ou son quartier.'
          : 'Mianatra manazava hafatra momba ny rano amin’ny fianakaviana, sekoly na fokontany.',
      quiz: '6 questions',
      points: 50,
      progress: 0,
    },
  ]

  const challenges = [
    {
      id: 1,
      title: language === 'FR' ? 'Chasse aux fuites' : 'Mitady fivoahan-drano',
      category: language === 'FR' ? 'Économie d’eau' : 'Fitsitsiana',
      objective:
        language === 'FR'
          ? 'Identifier et signaler au moins une fuite d’eau à la maison, à l’école ou dans la communauté.'
          : 'Mamantatra sy milaza fivoahan-drano iray farafahakeliny.',
      difficulty: language === 'FR' ? 'Facile' : 'Mora',
      points: 25,
      duration: language === 'FR' ? '30 minutes' : '30 minitra',
      instructions: [
        language === 'FR' ? 'Observe les robinets, tuyaux et points d’eau.' : 'Jereo ny robinet, tuyau ary toerana misy rano.',
        language === 'FR' ? 'Prends une photo ou écris ce que tu as trouvé.' : 'Makà sary na manorata izay hitanao.',
        language === 'FR' ? 'Explique comment la fuite peut être corrigée.' : 'Hazavao ny fomba fanamboarana azy.',
      ],
    },
    {
      id: 2,
      title: language === 'FR' ? 'Chaque goutte compte' : 'Sarobidy ny rano',
      category: language === 'FR' ? 'Challenge quotidien' : 'Fanamby isan’andro',
      objective:
        language === 'FR'
          ? 'Appliquer trois gestes simples pour économiser l’eau pendant une journée.'
          : 'Manao fihetsika telo hitsitsiana rano mandritra ny andro iray.',
      difficulty: language === 'FR' ? 'Facile' : 'Mora',
      points: 10,
      duration: language === 'FR' ? '1 jour' : '1 andro',
      instructions: [
        language === 'FR' ? 'Choisis trois gestes concrets.' : 'Misafidiana fihetsika telo.',
        language === 'FR' ? 'Note les moments où tu les appliques.' : 'Soraty ny fotoana anaovanao azy.',
        language === 'FR' ? 'Partage le résultat avec ton entourage.' : 'Zarao amin’ny manodidina ny vokatra.',
      ],
    },
    {
      id: 3,
      title: language === 'FR' ? 'Créer une affiche de sensibilisation' : 'Mamorona afisy',
      category: language === 'FR' ? 'Sensibilisation' : 'Fanentanana',
      objective:
        language === 'FR'
          ? 'Créer une affiche simple pour encourager les autres à protéger l’eau.'
          : 'Mamorona afisy tsotra hanentanana ny olona hiaro rano.',
      difficulty: language === 'FR' ? 'Moyen' : 'Antonony',
      points: 50,
      duration: language === 'FR' ? '2 heures' : '2 ora',
      instructions: [
        language === 'FR' ? 'Choisis un message clair.' : 'Misafidiana hafatra mazava.',
        language === 'FR' ? 'Ajoute un dessin ou une image.' : 'Ampio sary na kisary.',
        language === 'FR' ? 'Présente ton affiche à au moins 5 personnes.' : 'Asehoy olona 5 farafahakeliny.',
      ],
    },
    {
      id: 4,
      title: language === 'FR' ? 'Nettoyer un point d’eau' : 'Manadio toerana misy rano',
      category: language === 'FR' ? 'Action communautaire' : 'Asa iombonana',
      objective:
        language === 'FR'
          ? 'Organiser une petite action de nettoyage autour d’un point d’eau.'
          : 'Mikarakara fanadiovana kely manodidina toerana misy rano.',
      difficulty: language === 'FR' ? 'Difficile' : 'Sarotra',
      points: 100,
      duration: language === 'FR' ? 'Demi-journée' : 'Antsasaky ny andro',
      instructions: [
        language === 'FR' ? 'Identifie un lieu adapté et sûr.' : 'Fantaro toerana mety sy azo antoka.',
        language === 'FR' ? 'Mobilise quelques personnes.' : 'Antsoy olona vitsivitsy.',
        language === 'FR' ? 'Prends une photo avant/après.' : 'Makà sary aloha sy aorian’ny asa.',
      ],
    },
  ]

  const badges = [
    {
      title: language === 'FR' ? 'Éco-Geste' : 'Eco-Geste',
      icon: '💧',
      unlocked: true,
      condition: language === 'FR' ? '3 défis d’économie d’eau' : 'Fanamby fitsitsiana 3',
    },
    {
      title: language === 'FR' ? 'Protecteur des Sources' : 'Mpiaro Loharano',
      icon: '🌱',
      unlocked: true,
      condition: language === 'FR' ? '2 actions de protection' : 'Asa fiarovana 2',
    },
    {
      title: language === 'FR' ? 'Sensibilisateur' : 'Mpanentana',
      icon: '📣',
      unlocked: false,
      condition: language === 'FR' ? '5 actions de sensibilisation' : 'Fanentanana 5',
    },
    {
      title: language === 'FR' ? 'Ambassadeur de l’Eau' : 'Ambasadaoro Rano',
      icon: '🏅',
      unlocked: false,
      condition: language === 'FR' ? '10 défis validés' : 'Fanamby 10 voamarina',
    },
  ]

  const notifications = [
    language === 'FR'
      ? 'Ton activité “Créer une affiche” est prête pour validation.'
      : 'Vonona hohamarinina ny asa “Mamorona afisy”.',
    language === 'FR'
      ? 'Nouveau module disponible : Protection des sources d’eau.'
      : 'Misy module vaovao : Miaro loharano.',
    language === 'FR'
      ? 'Objectif de la semaine : sensibiliser 10 personnes.'
      : 'Tanjona amin’ity herinandro ity : manentana olona 10.',
  ]

  return {
    text,
    modules,
    challenges,
    badges,
    notifications,
  }
}
