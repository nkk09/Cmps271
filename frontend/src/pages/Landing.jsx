import { useState, useEffect } from "react"
import "../styles/landing.css"
import api from "../api"

function Landing({ user, onLogout }) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedDepartment, setSelectedDepartment] = useState("")
  const [courses, setCourses] = useState([])
  const [filteredCourses, setFilteredCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [departments, setDepartments] = useState([])

  // Fetch courses from backend
  useEffect(() => {
    const fetchCourses = async () => {
      setLoading(true)
      setError("")
      try {
        const allCourses = await api.getCourses()
        setCourses(allCourses || [])
        
        // Extract unique departments
        const depts = [...new Set(allCourses.map(c => c.department))]
        setDepartments(["All Departments", ...depts])
      } catch (err) {
        console.error("Failed to fetch courses:", err)
        setError("Failed to load courses")
        setCourses([])
      } finally {
        setLoading(false)
      }
    }

    fetchCourses()
  }, [])

  // Filter courses based on search and department
  useEffect(() => {
    let filtered = courses

    // Filter by department
    if (selectedDepartment && selectedDepartment !== "All Departments") {
      filtered = filtered.filter((course) => course.department === selectedDepartment)
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(
        (course) =>
          course.course_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
          course.course_name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    setFilteredCourses(filtered)
  }, [searchQuery, selectedDepartment, courses])

  return (
    <div className="landing-page">
      {/* Header */}
      <header className="landing-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="logo-title">📚 EduHub</h1>
          </div>
          <div className="profile-section">
            <div className="user-profile">
              <span className="username">{user?.username || "User"}</span>
              <button className="logout-btn" onClick={onLogout}>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="landing-main">
        {/* Search Bar Section */}
        <div className="search-section">
          <input
            type="text"
            className="search-bar"
            placeholder="🔍 Search courses or instructors..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Categories Section */}
        <div className="categories-section">
          <h2>Departments</h2>
          <div className="categories-grid">
            {departments.map((dept) => (
              <button
                key={dept}
                className={`category-btn ${(dept === "All Departments" && selectedDepartment === "") || selectedDepartment === dept ? "active" : ""}`}
                onClick={() => setSelectedDepartment(dept === "All Departments" ? "" : dept)}
              >
                {dept}
              </button>
            ))}
          </div>
        </div>

        {/* Courses Section */}
        <div className="courses-section">
          <h2>{selectedDepartment ? `${selectedDepartment} Courses` : "All Courses"}</h2>
          
          {error && <div className="error-message">{error}</div>}
          
          {loading ? (
            <div className="loading">Loading courses...</div>
          ) : filteredCourses.length > 0 ? (
            <div className="courses-grid">
              {filteredCourses.map((course) => (
                <div key={course.id} className="course-card">
                  <div className="course-content">
                    <h3>{course.course_number}</h3>
                    <p className="course-title">{course.course_name}</p>
                    <p className="department">🏢 {course.department}</p>
                    {course.credit_hours && (
                      <p className="credits">📖 {course.credit_hours} credits</p>
                    )}
                    {course.description && (
                      <p className="description">{course.description}</p>
                    )}
                    <button className="enroll-btn">View Sections & Reviews</button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-courses">
              <p>No courses found. Try adjusting your search or filter.</p>
            </div>
          )}
        </div>

        {/* Profile Section */}
        <div className="profile-card-section">
          <div className="profile-card">
            <h2>My Profile</h2>
            <div className="profile-info">
              <div className="profile-item">
                <label>Username (Anonymous):</label>
                <span>{user?.username || "N/A"}</span>
              </div>
              <div className="profile-item">
                <label>Role:</label>
                <span>{user?.role || "Student"}</span>
              </div>
              <div className="profile-item">
                <label>Member Since:</label>
                <span>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : "N/A"}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Landing
