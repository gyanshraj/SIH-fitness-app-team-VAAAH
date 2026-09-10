function DashboardPage({ user, workouts, progress }) {
  const totalMinutes = progress.reduce((sum, item) => sum + item.minutes, 0)
  const totalCalories = progress.reduce((sum, item) => sum + item.calories, 0)

  return (
    <main className="page">
      <h1>Welcome, {user?.name || 'User'}</h1>
      <p className="subtitle">Your fitness dashboard synced through API + SQL.</p>

      <section className="stats-grid">
        <article className="card stat-card">
          <h2>Weekly Workouts</h2>
          <p className="stat-number">{workouts.length}</p>
        </article>

        <article className="card stat-card">
          <h2>Total Minutes</h2>
          <p className="stat-number">{totalMinutes}</p>
        </article>

        <article className="card stat-card">
          <h2>Total Calories</h2>
          <p className="stat-number">{totalCalories}</p>
        </article>
      </section>
    </main>
  )
}

export default DashboardPage
