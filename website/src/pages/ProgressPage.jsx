import { useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function ProgressPage({ progress, onAddEntry, onDeleteEntry }) {
  const [date, setDate] = useState('')
  const [minutes, setMinutes] = useState('')
  const [calories, setCalories] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    try {
      await onAddEntry({
        date,
        minutes: Number(minutes),
        calories: Number(calories),
      })

      setDate('')
      setMinutes('')
      setCalories('')
    } catch (requestError) {
      setError(requestError.message || 'Unable to save progress entry.')
    }
  }

  return (
    <main className="page">
      <h1>Progress</h1>
      <p className="subtitle">Track progress entries synced to SQL.</p>

      <section className="card chart-card">
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={progress} margin={{ top: 20, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="minutes" stroke="#2563eb" name="Minutes" />
              <Line type="monotone" dataKey="calories" stroke="#16a34a" name="Calories" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card">
        <h2>Add Progress Entry</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Date
            <input type="date" value={date} onChange={(event) => setDate(event.target.value)} required />
          </label>

          <label>
            Minutes
            <input
              type="number"
              min="1"
              value={minutes}
              onChange={(event) => setMinutes(event.target.value)}
              required
            />
          </label>

          <label>
            Calories
            <input
              type="number"
              min="1"
              value={calories}
              onChange={(event) => setCalories(event.target.value)}
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit">Save Entry</button>
        </form>
      </section>

      <section className="card">
        <h2>Saved Entries</h2>
        {progress.length === 0 ? (
          <p>No progress entries yet.</p>
        ) : (
          <ul>
            {progress.map((entry) => (
              <li key={entry.id}>
                {entry.date} - {entry.minutes} mins - {entry.calories} calories{' '}
                <button type="button" className="secondary-btn" onClick={() => onDeleteEntry(entry.id)}>
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  )
}

export default ProgressPage
