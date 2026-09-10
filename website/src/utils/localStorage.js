const SESSION_KEY = 'fitness_api_session'

const parseSafely = (value, fallback) => {
  try {
    return value ? JSON.parse(value) : fallback
  } catch {
    return fallback
  }
}

export const loadSession = () => parseSafely(localStorage.getItem(SESSION_KEY), null)

export const saveSession = (session) => {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export const clearSession = () => {
  localStorage.removeItem(SESSION_KEY)
}
