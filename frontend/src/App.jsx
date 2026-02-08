import { useState, useEffect } from "react"
import Login from "./pages/Login"
import Me from "./pages/Me"

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [loading, setLoading] = useState(true)

  const backend = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      try {
        const resp = await fetch(`${backend}/auth/me`, {
          credentials: "include",
        })
        if (resp.ok) {
          setIsLoggedIn(true)
        }
      } catch (err) {
        console.error("Auth check error:", err)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [backend])

  if (loading) {
    return <div style={{ padding: "20px" }}>Loading...</div>
  }

  return isLoggedIn ? (
    <Me onLogout={() => setIsLoggedIn(false)} />
  ) : (
    <Login onLoginSuccess={() => setIsLoggedIn(true)} />
  )
}

export default App