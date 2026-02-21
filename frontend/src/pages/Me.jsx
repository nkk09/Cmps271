import { useState, useEffect } from "react"
import "../styles/me.css"
import api from "../api"

function Me({ onLogout }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    // Fetch current user from backend
    const fetchUser = async () => {
      try {
        const userData = await api.getCurrentUser()
        setUser(userData)
      } catch (err) {
        console.error("Error fetching user:", err)
        setError("Failed to load user info")
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [])

  const handleLogout = async () => {
    try {
      const backend = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"
      await fetch(`${backend}/auth/logout`, {
        method: "POST",
        credentials: "include",
      })
      onLogout()
    } catch (err) {
      console.error("Logout error:", err)
    }
  }

  return (
    <div className="me-page">
      <div className="me-container">
        {loading && <p>Loading...</p>}
        {error && <p className="error">{error}</p>}
        {user && (
          <div className="me-card">
            <h1>Welcome, {user.username}!</h1>
            <div className="user-info">
              <p>
                <strong>Anonymous Username:</strong> {user.username}
              </p>
              <p>
                <strong>Role:</strong> {user.role}
              </p>
              <p>
                <strong>Member Since:</strong> {new Date(user.created_at).toLocaleDateString()}
              </p>
            </div>

            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Me
