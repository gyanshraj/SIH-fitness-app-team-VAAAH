import { useState } from 'react'

function LoginPage({ onLogin, apiError }) {
  const [email, setEmail] = useState('demo@vaaah.com')
  const [password, setPassword] = useState('demo123')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setIsSubmitting(true)
    setError('')

    try {
      await onLogin({ email, password })
    } catch (requestError) {
      setError(requestError.message || 'Unable to login. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="page page-center">
      <section className="card login-card">
        <h1>VAAAH Fitness</h1>
        <p className="subtitle">Web app with Python API and SQL database.</p>

        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Enter email"
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter password"
              required
            />
          </label>

          {(error || apiError) && <p className="error">{error || apiError}</p>}

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="demo-box">
          <strong>Seed Demo Credentials</strong>
          <p>Email: demo@vaaah.com</p>
          <p>Password: demo123</p>
        </div>
      </section>
    </main>
  )
}

export default LoginPage
