import { useState } from 'react'

function LoginPage({ demoUser, onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()

    if (email === demoUser.email && password === demoUser.password) {
      onLogin({ name: demoUser.name, email: demoUser.email })
      return
    }

    setError('Invalid demo credentials. Please use the demo login details below.')
  }

  return (
    <main className="page page-center">
      <section className="card login-card">
        <h1>VAAAH Fitness Demo</h1>
        <p className="subtitle">Offline presentation mode (no backend required).</p>

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

          {error && <p className="error">{error}</p>}

          <button type="submit">Login to Demo</button>
        </form>

        <div className="demo-box">
          <strong>Demo Credentials</strong>
          <p>Email: {demoUser.email}</p>
          <p>Password: {demoUser.password}</p>
        </div>
      </section>
    </main>
  )
}

export default LoginPage
