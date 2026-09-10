function WorkoutPlanPage({ workouts }) {
  return (
    <main className="page">
      <h1>Workout Plan</h1>
      <p className="subtitle">Demo-friendly weekly routine (loaded from local JSON).</p>

      <section className="workout-grid">
        {workouts.map((workout) => (
          <article key={workout.id} className="card workout-card">
            <h2>
              {workout.day} - {workout.focus}
            </h2>
            <p>Duration: {workout.duration} mins</p>
            <ul>
              {workout.exercises.map((exercise) => (
                <li key={exercise}>{exercise}</li>
              ))}
            </ul>
          </article>
        ))}
      </section>
    </main>
  )
}

export default WorkoutPlanPage
