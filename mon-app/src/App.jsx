import { useEffect, useState } from 'react'

import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import ConfirmEmail from './pages/ConfirmEmail'
import Dashboard from './pages/Dashboard'

import './App.css'

function App() {
  const CURRENT_USER_KEY = 'waterChallengeCurrentUser'

  const getInitialPage = () => {
    const pathname = window.location.pathname

    if (pathname.startsWith('/confirm-email/')) {
      return 'confirm-email'
    }

    if (pathname === '/login') {
      return 'login'
    }

    if (pathname === '/signup') {
      return 'signup'
    }

    if (pathname === '/dashboard') {
      return 'dashboard'
    }

    return 'landing'
  }

  const getCurrentUser = () => {
    try {
      return JSON.parse(localStorage.getItem(CURRENT_USER_KEY)) || null
    } catch (error) {
      return null
    }
  }

  const savedUser = getCurrentUser()

  const [currentPage, setCurrentPage] = useState(() => {
    const initialPage = getInitialPage()

    if (initialPage === 'dashboard' && !savedUser) {
      return 'login'
    }

    return initialPage
  })

  const [user, setUser] = useState(savedUser)

  const updateBrowserUrl = (page) => {
    const routes = {
      landing: '/',
      login: '/login',
      signup: '/signup',
      dashboard: '/dashboard',
    }

    if (routes[page]) {
      window.history.pushState({}, '', routes[page])
    }
  }

  const handleNavigate = (page) => {
    if (page === 'dashboard' && !user) {
      setCurrentPage('login')
      updateBrowserUrl('login')
      return
    }

    setCurrentPage(page)
    updateBrowserUrl(page)
  }

  const handleLogin = (userData) => {
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userData))

    setUser(userData)
    setCurrentPage('dashboard')
    updateBrowserUrl('dashboard')
  }

  const handleLogout = () => {
    localStorage.removeItem(CURRENT_USER_KEY)
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')

    setUser(null)
    setCurrentPage('landing')
    updateBrowserUrl('landing')
  }

  useEffect(() => {
    const handlePopState = () => {
      const page = getInitialPage()

      if (page === 'dashboard' && !getCurrentUser()) {
        setCurrentPage('login')
        return
      }

      setCurrentPage(page)
    }

    window.addEventListener('popstate', handlePopState)

    return () => {
      window.removeEventListener('popstate', handlePopState)
    }
  }, [])

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

      {currentPage === 'dashboard' && user && (
        <Dashboard
          user={user}
          onLogout={handleLogout}
          onNavigate={handleNavigate}
        />
      )}
    </div>
  )
}

export default App