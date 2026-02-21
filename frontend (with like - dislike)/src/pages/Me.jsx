import { useState, useEffect } from "react"
import "../styles/me.css"

function Me({ onLogout }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const backend = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"

  useEffect(() => {
    // Fetch current user from backend
    const fetchUser = async () => {
      try {
        const resp = await fetch(`${backend}/auth/me`, {
          credentials: "include",
        })

        if (resp.ok) {
          const data = await resp.json()
          setUser(data.user)
        } else {
          setError("Failed to load user info")
        }
      } catch (err) {
        console.error("Error fetching user:", err)
        setError("Network error")
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [backend])

  const handleLogout = async () => {
    try {
      const resp = await fetch(`${backend}/auth/logout`, {
        method: "POST",
        credentials: "include",
      })
      if (resp.ok) {
        onLogout()
      }
    } catch (err) {
      console.error("Logout error:", err)
    }
  }

  if (loading) {
    return (
      <div className="me-page">
        <div className="me-container">
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (error || !user) {
    return (
      <div className="me-page">
        <div className="me-container">
          <p className="error">{error || "User not found"}</p>
          <button onClick={onLogout}>Back to Login</button>
        </div>
      </div>
    )
  }

  return (
    <div className="me-page">
      <div className="me-container">
        <div className="me-card">
          <h1>Welcome, {user.username}!</h1>
          <div className="user-info">
            <p>
              <strong>User ID:</strong> {user.user_id}
            </p>
            <p>
              <strong>Role:</strong> {user.role}
            </p>
          </div>

          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default Me
