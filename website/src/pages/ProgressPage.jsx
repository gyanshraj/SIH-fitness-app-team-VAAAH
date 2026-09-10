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

function ProgressPage({ progress, onAddEntry }) {
  const [date, setDate] = useState('')
  const [minutes, setMinutes] = useState('')
  const [calories, setCalories] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()

    onAddEntry({
      date,
      minutes: Number(minutes),
      calories: Number(calories),
    })

    setDate('')
    setMinutes('')
    setCalories('')
  }

  return (
    <main className="page">
      <h1>Progress</h1>
      <p className="subtitle">Track updates in localStorage for fully offline demo use.</p>

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

          <button type="submit">Save Entry</button>
        </form>
      </section>
    </main>
  )
}

export default ProgressPage
