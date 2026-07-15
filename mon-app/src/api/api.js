import axios from 'axios'

import {
  deleteCookie,
  getCookie,
  setCookie,
} from '../utils/cookies'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

let refreshPromise = null

const getAccessToken = () =>
  getCookie('accessToken') ||
  getCookie('access') ||
  localStorage.getItem('accessToken') ||
  ''

const getRefreshToken = () =>
  getCookie('refreshToken') ||
  getCookie('refresh') ||
  localStorage.getItem('refreshToken') ||
  ''

const clearSession = () => {
  deleteCookie('accessToken')
  deleteCookie('refreshToken')
  deleteCookie('access')
  deleteCookie('refresh')

  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('waterChallengeCurrentUser')
}

api.interceptors.request.use((config) => {
  const token = getAccessToken()

  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

const refreshAccessToken = async () => {
  const refresh = getRefreshToken()

  if (!refresh) {
    throw new Error('Aucun refresh token disponible.')
  }

  const response = await axios.post(
    `${API_BASE_URL}/auth/token/refresh/`,
    { refresh },
    { timeout: 30000 }
  )

  const access = response.data?.tokens?.access
  const nextRefresh =
    response.data?.tokens?.refresh || refresh

  if (!access) {
    throw new Error(
      "Le serveur n'a pas retourné de nouveau jeton d'accès."
    )
  }

  setCookie('accessToken', access, 5)
  setCookie('refreshToken', nextRefresh, 30)

  return access
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const status = error.response?.status
    const requestUrl = String(originalRequest?.url || '')

    const cannotRefresh =
      !originalRequest ||
      originalRequest.__waterChallengeRetried ||
      requestUrl.includes('/auth/login/') ||
      requestUrl.includes('/auth/token/refresh/')

    if (status !== 401 || cannotRefresh) {
      return Promise.reject(error)
    }

    originalRequest.__waterChallengeRetried = true

    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null
        })
      }

      const access = await refreshPromise

      originalRequest.headers = originalRequest.headers || {}
      originalRequest.headers.Authorization = `Bearer ${access}`

      return api(originalRequest)
    } catch (refreshError) {
      clearSession()

      window.dispatchEvent(
        new CustomEvent('waterchallenge:session-expired')
      )

      return Promise.reject(refreshError)
    }
  }
)

export const getApiErrorMessage = (
  error,
  fallback = 'Une erreur est survenue.'
) => {
  const data = error?.response?.data

  if (!error?.response) {
    return error?.message || fallback
  }

  if (typeof data === 'string') {
    return data
  }

  const directMessage =
    data?.erreur || data?.detail || data?.message

  if (directMessage) {
    return directMessage
  }

  if (data && typeof data === 'object') {
    const firstValue = Object.values(data)[0]

    if (Array.isArray(firstValue)) {
      return firstValue.join(' ')
    }

    if (typeof firstValue === 'string') {
      return firstValue
    }
  }

  return fallback
}

export const getMediaUrl = (mediaPath) => {
  if (!mediaPath) {
    return ''
  }

  const path = String(mediaPath)

  if (/^(https?:|data:|blob:)/i.test(path)) {
    return path
  }

  try {
    const apiUrl = new URL(API_BASE_URL, window.location.origin)
    const normalizedPath = path.startsWith('/') ? path : `/${path}`

    return new URL(normalizedPath, apiUrl.origin).href
  } catch {
    return path
  }
}

export { clearSession, getAccessToken, getRefreshToken }
export default api
