import { useState, useEffect, useCallback } from "react"
import Landing from "./pages/Landing"
import Reviews from "./pages/Reviews"
import Admin from "./pages/Admin"
import Me from "./pages/Me"
import Login from "./pages/Login"
import api from "./api"

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState("landing")
  const [reviewNavigation, setReviewNavigation] = useState({
    courseId: "",
    professorId: "",
    token: 0,
  })

  const isAdmin = user?.roles?.includes("admin")
  const isProfessor = user?.roles?.includes("professor")
  const myProfessorId = user?.professor?.id || ""

  const displayName = user?.student?.username || user?.professor?.first_name || "User"
  const displayRole = user?.roles?.[0] || ""

  const formatLabel = (text) => {
    if (!text) return ""
    return text
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase())
  }

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
    const params = new URLSearchParams(window.location.search)
    const callbackToken = params.get("token")
    const isCallbackPath = window.location.pathname === "/auth/callback"

    if (isCallbackPath && callbackToken) {
      api.token.set(callbackToken)
      window.history.replaceState({}, "", "/")
    }

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

  const handleOpenCourseReviews = (courseId) => {
    setReviewNavigation({ courseId, professorId: "", token: Date.now() })
    setCurrentPage("reviews")
  }

  const handleOpenProfessorReviews = (professorId) => {
    setReviewNavigation({ courseId: "", professorId, token: Date.now() })
    setCurrentPage("reviews")
  }

  if (loading) {
    return <div style={{ padding: "20px" }}>Loading...</div>
  }

  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <div>
      <nav
        style={{
          background: "linear-gradient(135deg, #8b1538, #5c0f25)",
          color: "white",
          padding: "0 30px",
          display: "flex",
          gap: "6px",
          alignItems: "center",
          height: "52px",
          position: "sticky",
          top: 0,
          zIndex: 200,
          boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
        }}
      >
        <span style={{ fontWeight: 700, fontSize: "16px", marginRight: "20px", opacity: 0.9 }}>
          📚 AfterClass
        </span>

        <NavButton active={currentPage === "landing"} onClick={() => setCurrentPage("landing")}>
          🏠 Courses
        </NavButton>

        <NavButton
          active={currentPage === "reviews"}
          onClick={() => {
            if (isProfessor && myProfessorId) {
              setReviewNavigation({
                courseId: "",
                professorId: myProfessorId,
                token: Date.now(),
              })
            } else {
              setReviewNavigation({
                courseId: "",
                professorId: "",
                token: Date.now(),
              })
            }
            setCurrentPage("reviews")
          }}
        >
          📝 Reviews
        </NavButton>

        <NavButton active={currentPage === "me"} onClick={() => setCurrentPage("me")}>
          👤 Profile
        </NavButton>

        {isAdmin && (
          <NavButton active={currentPage === "admin"} onClick={() => setCurrentPage("admin")}>
            ⚙️ Moderation
          </NavButton>
        )}

        <div style={{ flex: 1 }} />

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            marginRight: "10px",
            background: "rgba(255,255,255,0.14)",
            border: "1px solid rgba(255,255,255,0.18)",
            padding: "6px 12px",
            borderRadius: "999px",
            minHeight: "36px",
          }}
        >
          <span style={{ fontSize: "13px", fontWeight: 600, whiteSpace: "nowrap", lineHeight: 1 }}>
            👤 {displayName}
          </span>

          {displayRole && (
            <span
              style={{
                background: "rgba(255,255,255,0.92)",
                color: "#8b1538",
                padding: "2px 7px",
                borderRadius: "999px",
                fontSize: "11px",
                fontWeight: 700,
                whiteSpace: "nowrap",
                lineHeight: 1,
              }}
            >
              {formatLabel(displayRole)}
            </span>
          )}
        </div>

        <NavButton active={false} onClick={handleLogout}>
          Logout
        </NavButton>
      </nav>

      {currentPage === "landing" && (
        <Landing
          onViewCourseDetails={handleOpenCourseReviews}
          onViewProfessorReviews={handleOpenProfessorReviews}
        />
      )}

      {currentPage === "reviews" && (
        <Reviews
          user={user}
          initialCourseId={reviewNavigation.courseId}
          initialProfessorId={reviewNavigation.professorId}
          navigationToken={reviewNavigation.token}
        />
      )}

      {currentPage === "me" && <Me />}
      {currentPage === "admin" && <Admin user={user} />}
    </div>
  )
}

function NavButton({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: active ? "rgba(255,255,255,0.18)" : "transparent",
        color: "white",
        border: "none",
        padding: "8px 16px",
        borderRadius: "8px",
        cursor: "pointer",
        fontWeight: active ? 600 : 500,
        fontSize: "14px",
        transition: "background 0.2s ease, transform 0.2s ease",
        height: "36px",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        lineHeight: 1,
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </button>
  )
}

export default App