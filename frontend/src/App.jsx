import { useState, useEffect, useCallback } from "react"
import Landing from "./pages/Landing"
import Login from "./pages/Login"

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const backend = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"

  const checkAuth = useCallback(async () => {
    setLoading(true)
    try {
      const resp = await fetch(`${backend}/auth/me`, {
        credentials: "include",
      })
      if (resp.ok) {
        const data = await resp.json().catch(() => null)
        setUser(data)
      } else {
        setUser(null)
      }
    } catch (err) {
      console.error("Auth check error:", err)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [backend])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const handleLoginSuccess = async () => {
    // Re-check backend for session/user info after successful login
    await checkAuth()
  }

  const handleLogout = async () => {
    try {
      await fetch(`${backend}/auth/logout`, { method: "POST", credentials: "include" })
    } catch (e) {
      console.warn("Logout request failed", e)
    }
    setUser(null)
  }

  if (loading) {
    return <div style={{ padding: "20px" }}>Loading...</div>
  }

  return user ? (
    <Landing user={user} onLogout={handleLogout} />
  ) : (
    <Login onLoginSuccess={handleLoginSuccess} />
  )
}

export default App