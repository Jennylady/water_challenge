import { useState } from 'react'
import { motion } from 'framer-motion'
import api from '../api/api'
import { setCookie, getCookie } from '../utils/cookies'
import './LoginPage.css'

const translations = {
  FR: {
    title: 'Connexion',
    subtitle: 'Bienvenue chez Water Challenge',
    emailLabel: 'Email',
    emailPlaceholder: 'votre.email@example.com',
    passwordLabel: 'Mot de passe',
    passwordPlaceholder: 'Entrez votre mot de passe',
    loginBtn: 'Se connecter',
    loadingBtn: 'Connexion...',
    signupLink: "Pas encore inscrit ? S'inscrire",
    successMessage: 'Connexion réussie.',
    errorMessage: 'Email ou mot de passe incorrect.',
    networkError:
      'Impossible de contacter le serveur. Vérifiez que Django est lancé.',
    notActivatedError:
      "Votre compte n'est pas encore activé. Vérifiez votre email.",
    invalidResponse:
      "La réponse du serveur ne contient pas les informations attendues.",
  },

  MLG: {
    title: 'Fidirana',
    subtitle: "Tonga soa amin'ny Water Challenge",
    emailLabel: 'Email',
    emailPlaceholder: 'ny.email@example.com',
    passwordLabel: 'Tenimiafina',
    passwordPlaceholder: 'Ampidiro ny tenimiafinao',
    loginBtn: 'Hiditra',
    loadingBtn: 'Miditra...',
    signupLink: 'Tsy mbola nisoratra? Hisoratra',
    successMessage: 'Tafiditra soa aman-tsara.',
    errorMessage: 'Diso ny email na ny tenimiafina.',
    networkError:
      'Tsy afaka mifandray amin’ny serveur. Alefaso aloha Django.',
    notActivatedError:
      'Mbola tsy voamarina ny kaontinao. Jereo ny email-nao.',
    invalidResponse:
      'Tsy feno ny valin’ny serveur.',
  },
}

function LoginPage({ onNavigate, onLogin }) {
  const [form, setForm] = useState({
    email: '',
    password: '',
  })

  const [language, setLanguage] = useState('FR')
  const [message, setMessage] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const t = translations[language]

  const handleChange = ({ target }) => {
    const { name, value } = target

    setForm((previousForm) => ({
      ...previousForm,
      [name]: value,
    }))

    setMessage(null)
  }

  const getErrorMessage = (error) => {
    if (!error.response) {
      return error.message || t.networkError
    }

    const status = error.response.status
    const data = error.response.data

    if (typeof data === 'string') {
      return data
    }

    if (status === 403) {
      return data?.detail || data?.message || t.notActivatedError
    }

    if (status === 400 || status === 401) {
      return data?.detail || data?.message || t.errorMessage
    }

    if (data?.non_field_errors) {
      return Array.isArray(data.non_field_errors)
        ? data.non_field_errors.join(' ')
        : data.non_field_errors
    }

    if (data?.email) {
      return Array.isArray(data.email)
        ? data.email.join(' ')
        : data.email
    }

    if (data?.password) {
      return Array.isArray(data.password)
        ? data.password.join(' ')
        : data.password
    }

    return data?.detail || data?.message || t.networkError
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (isLoading) {
      return
    }

    setMessage(null)
    setIsLoading(true)

    try {
      const response = await api.post('/auth/login/', {
        email: form.email.trim().toLowerCase(),
        password: form.password,
      })

      console.log('Réponse complète du login :', response.data)

      const accessToken = response.data?.tokens?.access
      const refreshToken = response.data?.tokens?.refresh
      const userData = response.data?.user

      if (!accessToken || !refreshToken || !userData) {
        throw new Error(t.invalidResponse)
      }

      setCookie('accessToken', accessToken, 1)
      setCookie('refreshToken', refreshToken, 7)

      const savedAccessToken = getCookie('accessToken')

      if (!savedAccessToken) {
        throw new Error(
          "Le jeton d'accès n'a pas pu être enregistré dans les cookies."
        )
      }

      localStorage.setItem(
        'waterChallengeCurrentUser',
        JSON.stringify(userData)
      )

      setMessage({
        type: 'success',
        text: t.successMessage,
      })

      setForm({
        email: '',
        password: '',
      })

      window.setTimeout(() => {
        onLogin(userData)
      }, 400)
    } catch (error) {
      console.error('Erreur de connexion :', error)

      setMessage({
        type: 'error',
        text: getErrorMessage(error),
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      <motion.button
        type="button"
        className="back-arrow-btn"
        onClick={() => onNavigate('landing')}
        disabled={isLoading}
        title="Retour"
        aria-label="Retour à l'accueil"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
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
            <button
              type="button"
              className="login-logo"
              onClick={() => onNavigate('landing')}
              disabled={isLoading}
            >
              <span className="login-logo-mark">W</span>
              <span>Water Challenge</span>
            </button>

            <div className="login-language">
              {['FR', 'MLG'].map((lang) => (
                <button
                  key={lang}
                  type="button"
                  className={language === lang ? 'active' : ''}
                  onClick={() => setLanguage(lang)}
                  disabled={isLoading}
                  aria-pressed={language === lang}
                >
                  {lang}
                </button>
              ))}
            </div>
          </div>

          <h1>{t.title}</h1>
          <p className="login-subtitle">{t.subtitle}</p>

          {message && (
            <div
              className={`login-message ${message.type}`}
              role={message.type === 'error' ? 'alert' : 'status'}
            >
              {message.text}
            </div>
          )}

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">{t.emailLabel}</label>

              <input
                id="email"
                name="email"
                type="email"
                value={form.email}
                placeholder={t.emailPlaceholder}
                onChange={handleChange}
                disabled={isLoading}
                autoComplete="email"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">{t.passwordLabel}</label>

              <input
                id="password"
                name="password"
                type="password"
                value={form.password}
                placeholder={t.passwordPlaceholder}
                onChange={handleChange}
                disabled={isLoading}
                autoComplete="current-password"
                required
              />
            </div>

            <button
              type="submit"
              className="login-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="login-btn-loader-content">
                  <span className="login-loader" aria-hidden="true" />
                  {t.loadingBtn}
                </span>
              ) : (
                t.loginBtn
              )}
            </button>
          </form>

          <div className="login-footer">
            <button
              type="button"
              className="link-btn"
              onClick={() => onNavigate('signup')}
              disabled={isLoading}
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