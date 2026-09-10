import { useEffect, useMemo, useState } from 'react'
import { BrowserRouter, Link, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import './App.css'
import {
  addProgress,
  addWorkout,
  deleteProgress,
  deleteWorkout,
  getProfile,
  getProgress,
  getWorkouts,
  login,
} from './api/client'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import ProgressPage from './pages/ProgressPage'
import WorkoutPlanPage from './pages/WorkoutPlanPage'
import { clearSession, loadSession, saveSession } from './utils/localStorage'

function ProtectedRoute({ isLoggedIn }) {
  return isLoggedIn ? <Outlet /> : <Navigate to="/login" replace />
}

function AppLayout({ userName, onLogout }) {
  return (
    <>
      <header className="app-header">
        <div>
          <strong>VAAAH Fitness</strong>
          <p>Web + Python API</p>
        </div>

        <nav>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/workout-plan">Workout Plan</Link>
          <Link to="/progress">Progress</Link>
          <a href="/student-fitness.html" target="_blank" rel="noreferrer" style={{ color: '#38bdf8', fontWeight: 600 }}>
            Student Fitness (₹20 Vault)
          </a>
        </nav>

        <div className="header-actions">
          <span>{userName}</span>
          <button type="button" onClick={onLogout} className="secondary-btn">
            Logout
          </button>
        </div>
      </header>
      <Outlet />
    </>
  )
}

function App() {
  const [session, setSession] = useState(() => loadSession())
  const [workouts, setWorkouts] = useState([])
  const [progress, setProgress] = useState([])
  const [isBootstrapping, setIsBootstrapping] = useState(() => Boolean(loadSession()?.token))
  const [apiError, setApiError] = useState('')

  const isLoggedIn = useMemo(() => Boolean(session?.token), [session])

  useEffect(() => {
    const initialize = async () => {
      if (!session?.token) {
        setIsBootstrapping(false)
        return
      }

      try {
        const [profile, workoutsResponse, progressResponse] = await Promise.all([
          getProfile(session.token),
          getWorkouts(session.token),
          getProgress(session.token),
        ])

        const nextSession = { token: session.token, user: profile }
        setSession(nextSession)
        saveSession(nextSession)
        setWorkouts(workoutsResponse)
        setProgress(progressResponse)
        setApiError('')
      } catch {
        setSession(null)
        clearSession()
        setWorkouts([])
        setProgress([])
        setApiError('Session expired. Please login again.')
      } finally {
        setIsBootstrapping(false)
      }
    }

    initialize()
  }, [session?.token])

  const handleLogin = async (credentials) => {
    const data = await login(credentials)
    const nextSession = { token: data.token, user: data.user }
    setSession(nextSession)
    saveSession(nextSession)
    setApiError('')

    const [workoutsResponse, progressResponse] = await Promise.all([
      getWorkouts(nextSession.token),
      getProgress(nextSession.token),
    ])

    setWorkouts(workoutsResponse)
    setProgress(progressResponse)
  }

  const handleLogout = () => {
    setSession(null)
    clearSession()
    setWorkouts([])
    setProgress([])
  }

  const handleAddProgress = async (entry) => {
    const saved = await addProgress(session.token, entry)
    setProgress((current) => [...current, saved].sort((left, right) => left.date.localeCompare(right.date)))
  }

  const handleDeleteProgress = async (entryId) => {
    await deleteProgress(session.token, entryId)
    setProgress((current) => current.filter((entry) => entry.id !== entryId))
  }

  const handleAddWorkout = async (workout) => {
    const saved = await addWorkout(session.token, workout)
    setWorkouts((current) => [...current, saved])
  }

  const handleDeleteWorkout = async (workoutId) => {
    await deleteWorkout(session.token, workoutId)
    setWorkouts((current) => current.filter((workout) => workout.id !== workoutId))
  }

  if (isBootstrapping) {
    return (
      <main className="page page-center">
        <section className="card login-card">
          <h1>Loading...</h1>
        </section>
      </main>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            isLoggedIn ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LoginPage onLogin={handleLogin} apiError={apiError} />
            )
          }
        />

        <Route element={<ProtectedRoute isLoggedIn={isLoggedIn} />}>
          <Route
            element={
              <AppLayout
                userName={session?.user?.name || 'Demo User'}
                onLogout={handleLogout}
              />
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage user={session?.user} workouts={workouts} progress={progress} />} />
            <Route
              path="/workout-plan"
              element={<WorkoutPlanPage workouts={workouts} onAddWorkout={handleAddWorkout} onDeleteWorkout={handleDeleteWorkout} />}
            />
            <Route
              path="/progress"
              element={<ProgressPage progress={progress} onAddEntry={handleAddProgress} onDeleteEntry={handleDeleteProgress} />}
            />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to={isLoggedIn ? '/dashboard' : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
