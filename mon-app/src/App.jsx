import { useEffect, useState } from 'react'

import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import ConfirmEmail from './pages/ConfirmEmail'
import Dashboard from './pages/Dashboard'

import { accountApi } from './api/services'
import { getCookie, deleteCookie } from './utils/cookies'

import './App.css'

const PROTECTED_ROUTES = ['dashboard']
const CURRENT_USER_KEY = 'waterChallengeCurrentUser'

function App() {
  const isAuthenticated = () =>
    Boolean(getCookie('accessToken') || getCookie('refreshToken'))

  const getInitialPage = () => {
    const pathname = window.location.pathname

    if (pathname.startsWith('/confirm-email/')) {
      return 'confirm-email'
    }

    if (
      pathname === '/dashboard' ||
      pathname.startsWith('/dashboard/')
    ) {
      return 'dashboard'
    }

    const routes = {
      '/': 'landing',
      '/login': 'login',
      '/signup': 'signup',
    }

    return routes[pathname] || 'landing'
  }

  const getCurrentUser = () => {
    try {
      const savedUser = localStorage.getItem(CURRENT_USER_KEY)

      return savedUser ? JSON.parse(savedUser) : null
    } catch (error) {
      console.error(
        "Impossible de récupérer l'utilisateur enregistré :",
        error
      )

      localStorage.removeItem(CURRENT_USER_KEY)

      return null
    }
  }

  const resolveAllowedPage = (page) => {
    if (
      PROTECTED_ROUTES.includes(page) &&
      !isAuthenticated()
    ) {
      return 'login'
    }

    return page
  }

  const [user, setUser] = useState(() => {
    if (!isAuthenticated()) {
      return null
    }

    return getCurrentUser()
  })

  const [currentPage, setCurrentPage] = useState(() => {
    return resolveAllowedPage(getInitialPage())
  })

  const [isResolvingSession, setIsResolvingSession] = useState(
    () => isAuthenticated()
  )

  const updateBrowserUrl = (page, replace = false) => {
    const routes = {
      landing: '/',
      login: '/login',
      signup: '/signup',
      dashboard: '/dashboard',
    }

    const pathname = routes[page]

    if (!pathname) {
      return
    }

    if (replace) {
      window.history.replaceState({}, '', pathname)
    } else {
      window.history.pushState({}, '', pathname)
    }
  }

  const handleNavigate = (page) => {
    const allowedPage = resolveAllowedPage(page)

    setCurrentPage(allowedPage)
    updateBrowserUrl(allowedPage)
  }

  const handleLogin = (userData) => {
    if (!userData) {
      console.error(
        "Aucune donnée utilisateur reçue après la connexion."
      )

      return
    }

    localStorage.setItem(
      CURRENT_USER_KEY,
      JSON.stringify(userData)
    )

    setUser(userData)
    setCurrentPage('dashboard')
    updateBrowserUrl('dashboard', true)
  }

  const handleUserUpdate = (updatedUser) => {
    if (!updatedUser) {
      return
    }

    localStorage.setItem(
      CURRENT_USER_KEY,
      JSON.stringify(updatedUser)
    )
    setUser(updatedUser)
  }

  const handleLogout = () => {
    localStorage.removeItem(CURRENT_USER_KEY)
    localStorage.removeItem('user')

    deleteCookie('accessToken')
    deleteCookie('refreshToken')
    deleteCookie('access')
    deleteCookie('refresh')

    setUser(null)
    setCurrentPage('landing')
    updateBrowserUrl('landing', true)
  }

  useEffect(() => {
    let isMounted = true

    const restoreAuthenticatedUser = async () => {
      if (!isAuthenticated()) {
        if (isMounted) {
          setIsResolvingSession(false)
        }
        return
      }

      try {
        const authenticatedUser = await accountApi.me()

        if (!isMounted) {
          return
        }

        localStorage.setItem(
          CURRENT_USER_KEY,
          JSON.stringify(authenticatedUser)
        )
        setUser(authenticatedUser)
      } catch (error) {
        console.error(
          "Impossible de restaurer la session utilisateur :",
          error
        )
      } finally {
        if (isMounted) {
          setIsResolvingSession(false)
        }
      }
    }

    restoreAuthenticatedUser()

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    const handlePopState = () => {
      const requestedPage = getInitialPage()
      const allowedPage = resolveAllowedPage(requestedPage)

      setCurrentPage(allowedPage)

      if (requestedPage !== allowedPage) {
        updateBrowserUrl(allowedPage, true)
      }
    }

    window.addEventListener('popstate', handlePopState)

    return () => {
      window.removeEventListener(
        'popstate',
        handlePopState
      )
    }
  }, [])

  useEffect(() => {
    const handleSessionExpired = () => {
      handleLogout()
      setCurrentPage('login')
      updateBrowserUrl('login', true)
    }

    window.addEventListener(
      'waterchallenge:session-expired',
      handleSessionExpired
    )

    return () => {
      window.removeEventListener(
        'waterchallenge:session-expired',
        handleSessionExpired
      )
    }
  }, [])

  useEffect(() => {
    if (
      PROTECTED_ROUTES.includes(currentPage) &&
      !isAuthenticated()
    ) {
      localStorage.removeItem(CURRENT_USER_KEY)

      setUser(null)
      setCurrentPage('login')
      updateBrowserUrl('login', true)
    }
  }, [currentPage])

  return (
    <div className="app">
      {currentPage === 'landing' && (
        <LandingPage onNavigate={handleNavigate} />
      )}

      {currentPage === 'login' && (
        <LoginPage
          onNavigate={handleNavigate}
          onLogin={handleLogin}
        />
      )}

      {currentPage === 'signup' && (
        <SignupPage onNavigate={handleNavigate} />
      )}

      {currentPage === 'confirm-email' && (
        <ConfirmEmail onNavigate={handleNavigate} />
      )}

      {currentPage === 'dashboard' &&
        isAuthenticated() &&
        isResolvingSession &&
        !user && (
          <div className="app-session-loading" role="status">
            <span className="app-session-spinner" aria-hidden="true" />
            <p>Récupération de votre espace…</p>
          </div>
        )}

      {currentPage === 'dashboard' &&
        isAuthenticated() &&
        user && (
          <Dashboard
            user={user}
            onLogout={handleLogout}
            onUserUpdate={handleUserUpdate}
          />
        )}
    </div>
  )
}

export default App
