import { useState, useEffect, useCallback } from "react"
import Landing from "./pages/Landing"
import Reviews from "./pages/Reviews"
import Login from "./pages/Login"
import api from "./api"

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState("landing") // landing or reviews

  const checkAuth = useCallback(async () => {
    setLoading(true)
    try {
      const userData = await api.getCurrentUser()
      setUser(userData)
    } catch (err) {
      console.error("Auth check error:", err)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const handleLoginSuccess = async () => {
    // Re-check backend for session/user info after successful login
    setLoading(true)
    try {
      const userData = await api.getCurrentUser()
      setUser(userData)
    } catch (err) {
      console.error("Auth check error after login:", err)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await fetch(`${import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"}/auth/logout`, { 
        method: "POST", 
        credentials: "include" 
      })
    } catch (e) {
      console.warn("Logout request failed", e)
    }
    setUser(null)
  }

  if (loading) {
    return <div style={{ padding: "20px" }}>Loading...</div>
  }

  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  // User is logged in - show Landing or Reviews page
  return (
    <div>
      <nav className="top-nav" style={{ 
        background: "#333", 
        color: "white", 
        padding: "15px 20px", 
        display: "flex", 
        gap: "20px",
        alignItems: "center"
      }}>
        <button 
          onClick={() => setCurrentPage("landing")}
          style={{
            background: currentPage === "landing" ? "#667eea" : "transparent",
            color: "white",
            border: "none",
            padding: "8px 15px",
            borderRadius: "5px",
            cursor: "pointer"
          }}
        >
          🏠 Courses
        </button>
        <button 
          onClick={() => setCurrentPage("reviews")}
          style={{
            background: currentPage === "reviews" ? "#667eea" : "transparent",
            color: "white",
            border: "none",
            padding: "8px 15px",
            borderRadius: "5px",
            cursor: "pointer"
          }}
        >
          📝 Reviews
        </button>
      </nav>
      
      {currentPage === "landing" && <Landing user={user} onLogout={handleLogout} />}
      {currentPage === "reviews" && <Reviews user={user} />}
    </div>
  )
}

export default App