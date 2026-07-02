import { useState } from 'react'
import { motion } from 'framer-motion'
import './LoginPage.css'

function LoginPage({ onNavigate }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [language, setLanguage] = useState('FR')
  const [message, setMessage] = useState({ type: '', text: '' })

  const USERS_STORAGE_KEY = 'waterChallengeUsers'
  const CURRENT_USER_KEY = 'waterChallengeCurrentUser'

  const content = {
    FR: {
      title: 'Connexion',
      subtitle: 'Bienvenue chez Water Challenge',
      emailLabel: 'Email',
      emailPlaceholder: 'votre.email@example.com',
      passwordLabel: 'Mot de passe',
      passwordPlaceholder: 'Entrez votre mot de passe',
      loginBtn: 'Se connecter',
      signupLink: "Pas encore inscrit ? S'inscrire",
      backHome: "Retour à l'accueil",
      successMessage: 'Connexion réussie.',
      errorMessage: 'Email ou mot de passe incorrect.',
      emptyStorageMessage: "Aucun compte n'est encore enregistré. Veuillez d'abord vous inscrire.",
    },
    MLG: {
      title: 'Fidirana',
      subtitle: "Tonga soa amin'ny Water Challenge",
      emailLabel: 'Email',
      emailPlaceholder: 'ny.email@example.com',
      passwordLabel: 'Tenimiafina',
      passwordPlaceholder: 'Ampidiro ny tenimiafinao',
      loginBtn: 'Hiditra',
      signupLink: 'Tsy mbola nisoratra? Hisoratra',
      backHome: "Miverina amin'ny pejy fandraisana",
      successMessage: 'Tafiditra soa aman-tsara.',
      errorMessage: 'Diso ny email na ny tenimiafina.',
      emptyStorageMessage: 'Tsy mbola misy kaonty voatahiry. Misorata anarana aloha.',
    },
  }

  const t = content[language]

  const getSavedUsers = () => {
    try {
      return JSON.parse(localStorage.getItem(USERS_STORAGE_KEY)) || []
    } catch (error) {
      return []
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setMessage({ type: '', text: '' })

    const users = getSavedUsers()

    if (users.length === 0) {
      setMessage({
        type: 'error',
        text: t.emptyStorageMessage,
      })
      return
    }

    const cleanEmail = email.trim().toLowerCase()

    const foundUser = users.find((user) => {
      return (
        user.email?.trim().toLowerCase() === cleanEmail &&
        user.motDePasse === password
      )
    })

    if (!foundUser) {
      setMessage({
        type: 'error',
        text: t.errorMessage,
      })
      return
    }

    const connectedUser = {
      id: foundUser.id,
      nom: foundUser.nom,
      prenom: foundUser.prenom,
      email: foundUser.email,
      telephone: foundUser.telephone,
      dateNaissance: foundUser.dateNaissance,
      scoutType: foundUser.scoutType,
      section: foundUser.section,
      position: foundUser.position,
      fivondronana: foundUser.fivondronana,
      faritra: foundUser.faritra,
      diosezy: foundUser.diosezy,
      connectedAt: new Date().toISOString(),
    }

    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(connectedUser))

    setMessage({
      type: 'success',
      text: t.successMessage,
    })

    setEmail('')
    setPassword('')

    setTimeout(() => {
      onNavigate('dashboard')
    }, 600)
  }

  return (
    <div className="login-page">
      <motion.button
        className="back-arrow-btn"
        onClick={() => onNavigate('landing')}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        type="button"
        title="Retour"
      >
        ←
      </motion.button>

      <motion.div
        className="login-container"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.65, delay: 0.2 }}
      >
        <div className="login-box">
          <div className="form-header">
            <div className="login-logo" onClick={() => onNavigate('landing')}>
              <span className="login-logo-mark">W</span>
              <span>Water Challenge</span>
            </div>

            <div className="login-language">
              <button
                type="button"
                className={language === 'FR' ? 'active' : ''}
                onClick={() => setLanguage('FR')}
              >
                FR
              </button>

              <button
                type="button"
                className={language === 'MLG' ? 'active' : ''}
                onClick={() => setLanguage('MLG')}
              >
                MLG
              </button>
            </div>
          </div>

          <h1>{t.title}</h1>
          <p className="login-subtitle">{t.subtitle}</p>

          {message.text && (
            <div className={`login-message ${message.type}`}>
              {message.text}
            </div>
          )}

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="email">{t.emailLabel}</label>
              <input
                id="email"
                type="email"
                placeholder={t.emailPlaceholder}
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  setMessage({ type: '', text: '' })
                }}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">{t.passwordLabel}</label>
              <input
                id="password"
                type="password"
                placeholder={t.passwordPlaceholder}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value)
                  setMessage({ type: '', text: '' })
                }}
                required
              />
            </div>

            <button type="submit" className="login-btn">
              {t.loginBtn}
            </button>
          </form>

          <div className="login-footer">
            <button
              type="button"
              className="link-btn"
              onClick={() => onNavigate('signup')}
            >
              {t.signupLink}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default LoginPage