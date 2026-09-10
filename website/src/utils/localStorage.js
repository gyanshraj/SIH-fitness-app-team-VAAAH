const SESSION_KEY = 'fitness_demo_session'
const PROGRESS_KEY = 'fitness_demo_progress'

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

export const loadProgress = (defaultProgress) =>
  parseSafely(localStorage.getItem(PROGRESS_KEY), defaultProgress)

export const saveProgress = (progress) => {
  localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress))
}
