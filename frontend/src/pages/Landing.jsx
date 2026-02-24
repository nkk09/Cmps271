import { useState, useEffect } from "react"
import "../styles/landing.css"
import api from "../api"
import ReviewCard from "../components/ReviewCard"

// Assign a consistent emoji to each course based on its department prefix
const DEPT_EMOJI = {
  CMPS: "💻", MATH: "📐", PHYS: "⚛️", CHEM: "⚗️",
  BIOL: "🧬", ENGL: "📖", HIST: "🏛️", ECON: "📈",
  MGMT: "💼", MECH: "⚙️", ELEC: "⚡", CVLE: "🏗️",
}

function getCourseEmoji(course) {
  const prefix = (course.code || "").split(" ")[0].toUpperCase()
  return DEPT_EMOJI[prefix] || "📚"
}

function Landing({ user, onLogout }) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedDepartment, setSelectedDepartment] = useState("")
  const [courses, setCourses] = useState([])
  const [filteredCourses, setFilteredCourses] = useState([])
  const [departments, setDepartments] = useState([])
  const [loadingCourses, setLoadingCourses] = useState(true)
  const [courseError, setCourseError] = useState("")
  const [coursesOpen, setCoursesOpen] = useState(false)

  // Recent reviews (student's own reviews shown on landing)
  const [recentReviews, setRecentReviews] = useState([])
  const [loadingReviews, setLoadingReviews] = useState(false)

  const isStudent = user?.roles?.includes("student")

  // Fetch courses and departments
  useEffect(() => {
    const fetchData = async () => {
      setLoadingCourses(true)
      setCourseError("")
      try {
        const [allCourses, depts] = await Promise.all([
          api.courses.list({ limit: 100 }),
          api.courses.getDepartments(),
        ])
        setCourses(allCourses || [])
        setDepartments(depts || [])
      } catch (err) {
        console.error("Failed to fetch courses:", err)
        setCourseError("Failed to load courses")
        setCourses([])
      } finally {
        setLoadingCourses(false)
      }
    }
    fetchData()
  }, [])

  // Fetch the student's own recent reviews to show on the landing page
  useEffect(() => {
    if (!isStudent) return
    setLoadingReviews(true)
    api.users.getMyReviews({ limit: 5 })
      .then((data) => setRecentReviews(data || []))
      .catch(() => setRecentReviews([]))
      .finally(() => setLoadingReviews(false))
  }, [isStudent])

  // Filter courses locally on every search/department change
  useEffect(() => {
    let filtered = courses
    if (selectedDepartment) {
      filtered = filtered.filter((c) => c.department === selectedDepartment)
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (c) =>
          c.code.toLowerCase().includes(q) ||
          c.title.toLowerCase().includes(q)
      )
    }
    setFilteredCourses(filtered)
  }, [searchQuery, selectedDepartment, courses])

  const refreshReviews = async () => {
    const updated = await api.users.getMyReviews({ limit: 5 }).catch(() => [])
    setRecentReviews(updated || [])
  }

  // Like/Dislike a review, then refresh the list
  const handleInteract = async (reviewId, next, current) => {
    try {
      if (current === next) {
        await api.reviews.removeInteraction(reviewId)
      } else if (next === "like") {
        await api.reviews.like(reviewId)
      } else if (next === "dislike") {
        await api.reviews.dislike(reviewId)
      } else {
        await api.reviews.removeInteraction(reviewId)
      }
      await refreshReviews()
    } catch (err) {
      console.error("Interaction failed:", err)
    }
  }

  const handleDeleteReview = async (reviewId) => {
    if (!confirm("Delete this review?")) return
    try {
      await api.reviews.delete(reviewId)
      await refreshReviews()
    } catch (err) {
      console.error("Delete failed:", err)
    }
  }

  const handleEditReview = async (reviewId, newContent) => {
    try {
      await api.reviews.update(reviewId, { content: newContent })
      await refreshReviews()
    } catch (err) {
      console.error("Edit failed:", err)
    }
  }

  const username = user?.student?.username || user?.user?.id?.slice(0, 8) || "User"
  const role = user?.roles?.[0] || "student"
  const memberSince = user?.user?.created_at
    ? new Date(user.user.created_at).toLocaleDateString()
    : "N/A"

  return (
    <div className="landing-page">
      {/* Header */}
      <header className="landing-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="logo-title">📚 AfterClass</h1>
          </div>
          <div className="profile-section">
            <div className="user-profile">
              <span className="username">{username}</span>
              <button className="logout-btn" onClick={onLogout}>Logout</button>
            </div>
          </div>
        </div>
      </header>

      <main className="landing-main">
        {/* Search */}
        <div className="search-section">
          <input
            type="text"
            className="search-bar"
            placeholder="🔍 Search courses by code or title..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Department filter */}
        <div className="categories-section">
          <h2>Departments</h2>
          <div className="categories-grid">
            <button
              className={`category-btn ${selectedDepartment === "" ? "active" : ""}`}
              onClick={() => setSelectedDepartment("")}
            >
              All
            </button>
            {departments.map((dept) => (
              <button
                key={dept}
                className={`category-btn ${selectedDepartment === dept ? "active" : ""}`}
                onClick={() => setSelectedDepartment(dept)}
              >
                {dept}
              </button>
            ))}
          </div>
        </div>

        {/* Courses */}
        <div className="courses-section">
          <button
            className="section-toggle"
            onClick={() => setCoursesOpen((o) => !o)}
            aria-expanded={coursesOpen}
          >
            <h2 style={{ margin: 0 }}>{selectedDepartment ? `${selectedDepartment} Courses` : "All Courses"}</h2>
            <span className={`toggle-chevron ${coursesOpen ? "open" : ""}`}>▾</span>
          </button>
          {courseError && <div className="error-message">{courseError}</div>}
          {coursesOpen && loadingCourses ? (
            <div className="loading">Loading courses...</div>
          ) : coursesOpen && filteredCourses.length > 0 ? (
            <div className="courses-grid">
              {filteredCourses.map((course) => (
                <div key={course.id} className="course-card">
                  <div className="course-image">{getCourseEmoji(course)}</div>
                  <div className="course-content">
                    <h3>{course.code}</h3>
                    <p className="course-title">{course.title}</p>
                    <p className="department">🏢 {course.department}</p>
                    {course.description && (
                      <p className="description">{course.description}</p>
                    )}
                    {course.attributes?.length > 0 && (
                      <div className="course-attributes">
                        {course.attributes.map((attr) => (
                          <span key={attr} className="tag">{attr}</span>
                        ))}
                      </div>
                    )}
                    {course.average_rating != null && (
                      <div className="course-meta">
                        <span className="rating">⭐ {course.average_rating.toFixed(1)}</span>
                      </div>
                    )}
                    <button className="enroll-btn">View Sections &amp; Reviews</button>
                  </div>
                </div>
              ))}
            </div>
          ) : coursesOpen ? (
            <div className="no-courses">
              <p>No courses found. Try adjusting your search or filter.</p>
            </div>
          ) : null}
        </div>

        {/* My Recent Reviews — only shown to students */}
        {isStudent && (
          <div className="courses-section">
            <h2>My Recent Reviews</h2>
            {loadingReviews ? (
              <div className="loading">Loading reviews...</div>
            ) : recentReviews.length > 0 ? (
              <div style={{ display: "grid", gap: "1rem" }}>
                {recentReviews.map((review) => {
                  const myInteraction = review.my_interaction ?? null
                  return (
                    <ReviewCard
                      key={review.id}
                      review={{
                        id: review.id,
                        course: review.section?.course?.code || "Course",
                        professor: review.section?.professor
                          ? `${review.section.professor.first_name} ${review.section.professor.last_name}`
                          : "Professor",
                        text: review.content,
                        likes: review.likes_count,
                        dislikes: review.dislikes_count,
                        createdAt: new Date(review.created_at).toLocaleDateString(),
                      }}
                      reaction={myInteraction}
                      onReact={(next) => handleInteract(review.id, next, myInteraction)}
                      disableInteract={true}
                      author={review.student?.username || "anonymous"}
                      isMyReview={true}
                      onDelete={() => handleDeleteReview(review.id)}
                      onEdit={(newContent) => handleEditReview(review.id, newContent)}
                    />
                  )
                })}
              </div>
            ) : (
              <div className="no-courses">
                <p>You haven&apos;t written any reviews yet. Head to the Reviews tab to get started!</p>
              </div>
            )}
          </div>
        )}

        {/* Profile card */}
        <div className="profile-card-section">
          <div className="profile-card">
            <h2>My Profile</h2>
            <div className="profile-info">
              <div className="profile-item">
                <label>Username (Anonymous)</label>
                <span>{username}</span>
              </div>
              <div className="profile-item">
                <label>Role</label>
                <span>{role}</span>
              </div>
              <div className="profile-item">
                <label>Member Since</label>
                <span>{memberSince}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Landing
