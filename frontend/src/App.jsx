// src/App.jsx
import { useState, useEffect, useCallback } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import CourseList from "./components/CourseList";
import Course from "./components/Course";

function App() {
  const [user, setUser] = useState(null); // stores authenticated user info
  const [loading, setLoading] = useState(true); // loading state while checking auth
  const backend = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

  // Check if the user is logged in
  const checkAuth = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${backend}/auth/me`, { credentials: "include" });
      if (resp.ok) {
        const data = await resp.json().catch(() => null);
        setUser(data); // store user info
      } else {
        setUser(null);
      }
    } catch (err) {
      console.error("Auth check error:", err);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [backend]);

  // On app load, check auth
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Called after successful login
  const handleLoginSuccess = async () => {
    await checkAuth(); // refresh user info
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await fetch(`${backend}/auth/logout`, { method: "POST", credentials: "include" });
    } catch (e) {
      console.warn("Logout failed:", e);
    }
    setUser(null);
  };

  if (loading) return <div>Loading...</div>; // show while auth check in progress

  return user ? (
    // Router for navigating courses/reviews after login
    <Router>
      <Landing user={user} onLogout={handleLogout} />
      <Routes>
        <Route path="/" element={<CourseList />} />
        <Route path="/courses/:id" element={<Course />} />
      </Routes>
    </Router>
  ) : (
    <Login onLoginSuccess={handleLoginSuccess} />
  );
}

export default App;

/*Notes for later:
You can wrap routes in a ProtectedRoute component to enforce login.

You may want to add a 404 route.

Loading and error handling can be improved with spinners or alerts. */