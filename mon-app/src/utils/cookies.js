const COOKIE_PATH = '/'

export const setCookie = (name, value, days = 7) => {
  if (!name || value === undefined || value === null) {
    return false
  }

  const maxAge = Math.max(
    0,
    Math.floor(Number(days) * 24 * 60 * 60)
  )

  const secure =
    typeof window !== 'undefined' &&
    window.location.protocol === 'https:'

  const cookieOptions = [
    `${encodeURIComponent(name)}=${encodeURIComponent(String(value))}`,
    `Path=${COOKIE_PATH}`,
    `Max-Age=${maxAge}`,
    'SameSite=Lax',
  ]

  if (secure) {
    cookieOptions.push('Secure')
  }

  document.cookie = cookieOptions.join('; ')

  return getCookie(name) === String(value)
}

export const getCookie = (name) => {
  if (!name || typeof document === 'undefined') {
    return null
  }

  const encodedName = `${encodeURIComponent(name)}=`

  const cookie = document.cookie
    .split(';')
    .map((item) => item.trim())
    .find((item) => item.startsWith(encodedName))

  if (!cookie) {
    return null
  }

  try {
    return decodeURIComponent(
      cookie.substring(encodedName.length)
    )
  } catch (error) {
    console.error(
      `Impossible de décoder le cookie "${name}" :`,
      error
    )

    return null
  }
}

export const deleteCookie = (name) => {
  if (!name || typeof document === 'undefined') {
    return
  }

  const secure =
    typeof window !== 'undefined' &&
    window.location.protocol === 'https:'

  const cookieOptions = [
    `${encodeURIComponent(name)}=`,
    `Path=${COOKIE_PATH}`,
    'Max-Age=0',
    'Expires=Thu, 01 Jan 1970 00:00:00 GMT',
    'SameSite=Lax',
  ]

  if (secure) {
    cookieOptions.push('Secure')
  }

  document.cookie = cookieOptions.join('; ')
}