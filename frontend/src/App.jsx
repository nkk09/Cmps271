import { useState, useEffect, useCallback } from "react"
import Landing from "./pages/Landing"
import Reviews from "./pages/Reviews"
import Login from "./pages/Login"
import api from "./api"

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState("landing")

  const checkAuth = useCallback(async () => {
    if (!api.auth.isLoggedIn()) {
      setLoading(false)
      return
    }
    setLoading(true)
    try {
      const userData = await api.users.getMe()
      setUser(userData)
    } catch (err) {
      console.error("Auth check error:", err)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // ── Handle Entra OAuth callback ──────────────────────────────────────
    // After Microsoft login, the backend redirects to:
    //   FRONTEND_URL/auth/callback?token=<jwt>
    // We read it once, store it, then strip it from the URL.
    const params = new URLSearchParams(window.location.search)
    const callbackToken = params.get("token")
    const isCallbackPath = window.location.pathname === "/auth/callback"

    if (isCallbackPath && callbackToken) {
      api.token.set(callbackToken)
      // Clean the token out of the URL so it's not visible or bookmarkable
      window.history.replaceState({}, "", "/")
    }
    // ────────────────────────────────────────────────────────────────────

    checkAuth()

    const handleExpired = () => setUser(null)
    window.addEventListener("auth:expired", handleExpired)
    return () => window.removeEventListener("auth:expired", handleExpired)
  }, [checkAuth])

  const handleLoginSuccess = async () => {
    setLoading(true)
    try {
      const userData = await api.users.getMe()
      setUser(userData)
    } catch (err) {
      console.error("Auth check error after login:", err)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await api.auth.logout()
    setUser(null)
  }

  if (loading) {
    return <div style={{ padding: "20px" }}>Loading...</div>
  }

  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <div>
      <nav style={{
        background: "linear-gradient(135deg, #8b1538, #5c0f25)",
        color: "white",
        padding: "0 30px",
        display: "flex",
        gap: "4px",
        alignItems: "center",
        height: "52px",
        position: "sticky",
        top: 0,
        zIndex: 200,
        boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
      }}>
        <span style={{ fontWeight: 700, fontSize: "16px", marginRight: "20px", opacity: 0.9 }}>
          📚 AfterClass
        </span>
        <NavButton active={currentPage === "landing"} onClick={() => setCurrentPage("landing")}>
          🏠 Courses
        </NavButton>
        <NavButton active={currentPage === "reviews"} onClick={() => setCurrentPage("reviews")}>
          📝 Reviews
        </NavButton>
      </nav>

      {currentPage === "landing" && <Landing user={user} onLogout={handleLogout} />}
      {currentPage === "reviews" && <Reviews user={user} />}
    </div>
  )
}

function NavButton({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: active ? "rgba(255,255,255,0.2)" : "transparent",
        color: "white",
        border: "none",
        padding: "8px 16px",
        borderRadius: "6px",
        cursor: "pointer",
        fontWeight: active ? 600 : 400,
        fontSize: "14px",
        transition: "background 0.2s",
      }}
    >
      {children}
    </button>
  )
}

export default App