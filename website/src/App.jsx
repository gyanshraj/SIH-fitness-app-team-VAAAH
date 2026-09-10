import { useEffect, useMemo, useState } from 'react'
import { BrowserRouter, Link, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import './App.css'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import ProgressPage from './pages/ProgressPage'
import WorkoutPlanPage from './pages/WorkoutPlanPage'
import { DEFAULT_PROGRESS, DEMO_USER, WORKOUT_PLAN } from './data/mockData'
import {
  clearSession,
  loadProgress,
  loadSession,
  saveProgress,
  saveSession,
} from './utils/localStorage'

function ProtectedRoute({ isLoggedIn }) {
  return isLoggedIn ? <Outlet /> : <Navigate to="/login" replace />
}

function AppLayout({ userName, onLogout }) {
  return (
    <>
      <header className="app-header">
        <div>
          <strong>VAAAH Fitness</strong>
          <p>Offline Demo</p>
        </div>

        <nav>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/workout-plan">Workout Plan</Link>
          <Link to="/progress">Progress</Link>
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
  const [progress, setProgress] = useState(() => loadProgress(DEFAULT_PROGRESS))

  useEffect(() => {
    saveProgress(progress)
  }, [progress])

  const isLoggedIn = useMemo(() => Boolean(session), [session])

  const handleLogin = (user) => {
    setSession(user)
    saveSession(user)
  }

  const handleLogout = () => {
    setSession(null)
    clearSession()
  }

  const handleAddProgress = (entry) => {
    setProgress((current) =>
      [...current, entry].sort((left, right) => left.date.localeCompare(right.date)),
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            isLoggedIn ? <Navigate to="/dashboard" replace /> : <LoginPage demoUser={DEMO_USER} onLogin={handleLogin} />
          }
        />

        <Route element={<ProtectedRoute isLoggedIn={isLoggedIn} />}>
          <Route
            element={
              <AppLayout
                userName={session?.name || 'Demo User'}
                onLogout={handleLogout}
              />
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route
              path="/dashboard"
              element={<DashboardPage user={session} workouts={WORKOUT_PLAN} progress={progress} />}
            />
            <Route path="/workout-plan" element={<WorkoutPlanPage workouts={WORKOUT_PLAN} />} />
            <Route
              path="/progress"
              element={<ProgressPage progress={progress} onAddEntry={handleAddProgress} />}
            />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to={isLoggedIn ? '/dashboard' : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
