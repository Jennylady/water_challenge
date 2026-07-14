import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import api from '../api/api'
import './SignupPage.css'

function ConfirmEmailPage({ onNavigate }) {
  const [status, setStatus] = useState('loading')
  const [message, setMessage] = useState('Validation de votre email en cours...')

  const {token } = useMemo(() => {
    const parts = window.location.pathname.split('/').filter(Boolean)

    return {
      token: parts[1],
    }
  }, [])

  useEffect(() => {
    const confirmEmail = async () => {
      if (!token) {
        setStatus('error')
        setMessage('Lien de confirmation invalide.')
        return
      }

      try {
        const response = await api.post(`/auth/activate/`, { token })

        setStatus('success')
        setMessage(
          response.data?.message ||
            'Email confirmé avec succès. Vous pouvez maintenant vous connecter.'
        )
      } catch (error) {
        setStatus('error')

        const apiMessage =
          error?.response?.data?.message ||
          error?.response?.data?.detail ||
          'Lien de confirmation invalide ou expiré.'

        setMessage(apiMessage)
      }
    }

    confirmEmail()
  }, [token])

  return (
    <div className="confirm-email-page">
      <motion.div
        className="confirm-email-card"
        initial={{ opacity: 0, y: 26, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45 }}
      >
        <motion.div
          className={`confirm-email-icon ${status}`}
          initial={{ scale: 0.7, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.35 }}
        >
          {status === 'loading' && <span className="big-loader"></span>}
          {status === 'success' && '✓'}
          {status === 'error' && '!' }
        </motion.div>

        <h1>
          {status === 'loading' && 'Validation email'}
          {status === 'success' && 'Email confirmé'}
          {status === 'error' && 'Validation impossible'}
        </h1>

        <p>{message}</p>

        {status !== 'loading' && (
          <button
            type="button"
            className="btn-primary confirm-email-btn"
            onClick={() => onNavigate('login')}
          >
            Aller à la connexion
          </button>
        )}
      </motion.div>
    </div>
  )
}

export default ConfirmEmailPage