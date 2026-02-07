function LeftPanel() {
  return (
    <div className="left-panel">
      <div className="logo">
        <span className="logo-icon">📖</span>
        <div>
          <h3>AUB Course Review</h3>
          <p>Student Community Platform</p>
        </div>
      </div>

      <h1>Make Better Course Decisions Together</h1>
      <p className="subtitle">
        Join your fellow AUB students in sharing and discovering course reviews
        to navigate your academic journey with confidence.
      </p>

      <div className="features">
        <div>
          ⭐ <strong>Course Reviews</strong>
          <p>Read honest reviews from students who’ve taken the course</p>
        </div>
        <div>
          👥 <strong>Professor Insights</strong>
          <p>Learn about teaching styles and course expectations</p>
        </div>
        <div>
          💬 <strong>Community Forum</strong>
          <p>Discuss courses and connect with fellow students</p>
        </div>
        <div>
          📚 <strong>Smart Search</strong>
          <p>Find the perfect courses for your schedule and goals</p>
        </div>
      </div>

      <footer>© 2026 AUB Course Review. Made by students, for students.</footer>
    </div>
  )
}

export default LeftPanel
