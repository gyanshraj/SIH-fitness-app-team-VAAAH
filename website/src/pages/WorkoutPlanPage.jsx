import { useState } from 'react'

function WorkoutPlanPage({ workouts, onAddWorkout, onDeleteWorkout }) {
  const [day, setDay] = useState('')
  const [focus, setFocus] = useState('')
  const [duration, setDuration] = useState('')
  const [exercises, setExercises] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    const exerciseList = exercises
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)

    if (!exerciseList.length) {
      setError('Please add at least one exercise.')
      return
    }

    try {
      await onAddWorkout({
        day,
        focus,
        duration: Number(duration),
        exercises: exerciseList,
      })
      setDay('')
      setFocus('')
      setDuration('')
      setExercises('')
    } catch (requestError) {
      setError(requestError.message || 'Failed to add workout.')
    }
  }

  return (
    <main className="page">
      <h1>Workout Plan</h1>
      <p className="subtitle">Weekly routine stored in SQL through the Python API.</p>

      <section className="card">
        <h2>Add Workout</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Day
            <input value={day} onChange={(event) => setDay(event.target.value)} placeholder="Monday" required />
          </label>
          <label>
            Focus
            <input value={focus} onChange={(event) => setFocus(event.target.value)} placeholder="Upper Body" required />
          </label>
          <label>
            Duration (mins)
            <input
              type="number"
              min="1"
              value={duration}
              onChange={(event) => setDuration(event.target.value)}
              required
            />
          </label>
          <label>
            Exercises (comma separated)
            <input
              value={exercises}
              onChange={(event) => setExercises(event.target.value)}
              placeholder="Push-ups, Dumbbell Press"
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit">Save Workout</button>
        </form>
      </section>

      <section className="workout-grid">
        {workouts.map((workout) => (
          <article key={workout.id} className="card workout-card">
            <h2>
              {workout.day} - {workout.focus}
            </h2>
            <p>Duration: {workout.duration} mins</p>
            <ul>
              {workout.exercises.map((exercise) => (
                <li key={`${workout.id}-${exercise}`}>{exercise}</li>
              ))}
            </ul>
            <button type="button" className="secondary-btn" onClick={() => onDeleteWorkout(workout.id)}>
              Delete
            </button>
          </article>
        ))}
      </section>
    </main>
  )
}

export default WorkoutPlanPage
