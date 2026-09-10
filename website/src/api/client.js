const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

const request = async (path, { token, method = 'GET', body } = {}) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'X-Auth-Token': token } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  })

  if (!response.ok) {
    let message = 'Request failed.'
    try {
      const errorPayload = await response.json()
      message = errorPayload.detail || message
    } catch {
      // Ignore json parse errors
    }
    throw new Error(message)
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

export const login = (payload) => request('/auth/login', { method: 'POST', body: payload })

export const getProfile = (token) => request('/users/me', { token })

export const getWorkouts = (token) => request('/workouts', { token })

export const addWorkout = (token, payload) => request('/workouts', { token, method: 'POST', body: payload })

export const deleteWorkout = (token, workoutId) =>
  request(`/workouts/${workoutId}`, { token, method: 'DELETE' })

export const getProgress = (token) => request('/progress', { token })

export const addProgress = (token, payload) => request('/progress', { token, method: 'POST', body: payload })

export const deleteProgress = (token, entryId) =>
  request(`/progress/${entryId}`, { token, method: 'DELETE' })

export const getGoals = (token) => request('/goals', { token })
