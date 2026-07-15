const DASHBOARD_BASE_PATH = '/dashboard'

const normalizePathname = (pathname = '') => {
  const normalized = String(pathname || '').replace(/\/+$/, '')
  return normalized || '/'
}

const safeDecode = (value = '') => {
  try {
    return decodeURIComponent(value)
  } catch {
    return value
  }
}

const safeEncode = (value = '') =>
  encodeURIComponent(String(value || '').trim())

export const parseDashboardLocation = (
  locationObject = typeof window !== 'undefined'
    ? window.location
    : { pathname: DASHBOARD_BASE_PATH, search: '', hash: '' }
) => {
  const pathname = normalizePathname(locationObject.pathname)
  const searchParams = new URLSearchParams(locationObject.search || '')
  const moduleMatch = pathname.match(
    /^\/dashboard\/modules\/([^/]+)(?:\/(quiz|challenges))?$/i
  )

  if (moduleMatch) {
    const moduleSlug = safeDecode(moduleMatch[1])
    const moduleView = String(moduleMatch[2] || '').toLowerCase()
    const challengeId = String(searchParams.get('challengeId') || '').trim()

    return {
      isDashboard: true,
      section: moduleView === 'challenges' ? 'challenges' : 'learning',
      moduleSlug,
      view: moduleView === 'quiz' ? 'quiz' : 'read',
      challengeId,
      isModuleRoute: true,
    }
  }

  const hashSection = safeDecode(
    String(locationObject.hash || '').replace(/^#\/?/, '').trim().toLowerCase()
  )
  const querySection = String(searchParams.get('section') || '').trim().toLowerCase()
  const moduleSlug = String(
    searchParams.get('module') ||
      searchParams.get('moduleSlug') ||
      searchParams.get('module_slug') ||
      ''
  ).trim()

  return {
    isDashboard:
      pathname === DASHBOARD_BASE_PATH ||
      pathname.startsWith(`${DASHBOARD_BASE_PATH}/`),
    section: querySection || hashSection || 'dashboard',
    moduleSlug,
    view: searchParams.get('view') === 'quiz' ? 'quiz' : 'read',
    challengeId: String(searchParams.get('challengeId') || '').trim(),
    isModuleRoute: Boolean(moduleSlug),
  }
}

export const buildDashboardUrl = ({
  section = 'dashboard',
  moduleSlug = '',
  view = 'read',
  challengeId = '',
} = {}) => {
  const normalizedSection = String(section || 'dashboard').trim().toLowerCase()
  const normalizedModuleSlug = String(moduleSlug || '').trim()
  const normalizedChallengeId = String(challengeId || '').trim()

  if (normalizedModuleSlug) {
    const encodedSlug = safeEncode(normalizedModuleSlug)

    if (normalizedSection === 'challenges') {
      const searchParams = new URLSearchParams()

      if (normalizedChallengeId) {
        searchParams.set('challengeId', normalizedChallengeId)
      }

      const query = searchParams.toString()
      return `${DASHBOARD_BASE_PATH}/modules/${encodedSlug}/challenges${query ? `?${query}` : ''}#challenges`
    }

    const viewPart = view === 'quiz' ? '/quiz' : ''
    return `${DASHBOARD_BASE_PATH}/modules/${encodedSlug}${viewPart}#learning`
  }

  const searchParams = new URLSearchParams()

  if (normalizedSection === 'challenges' && normalizedChallengeId) {
    searchParams.set('section', 'challenges')
    searchParams.set('challengeId', normalizedChallengeId)
  }

  const query = searchParams.toString()
  const hash = `#${normalizedSection || 'dashboard'}`

  return `${DASHBOARD_BASE_PATH}${query ? `?${query}` : ''}${hash}`
}

export const pushDashboardUrl = (options, state = {}) => {
  if (typeof window === 'undefined') {
    return
  }

  window.history.pushState(state, '', buildDashboardUrl(options))
}

export const replaceDashboardUrl = (options, state = {}) => {
  if (typeof window === 'undefined') {
    return
  }

  window.history.replaceState(state, '', buildDashboardUrl(options))
}
