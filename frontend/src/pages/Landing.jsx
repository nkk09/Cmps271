import { useState, useEffect } from "react"
import "../styles/landing.css"
import ReviewCard from "../components/ReviewCard"

function Landing({ user, onLogout }) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [courses, setCourses] = useState([])
  const [filteredCourses, setFilteredCourses] = useState([])

  // ---------------- Like/Dislike mechanism (Sprint 2) ----------------
  // Replace these sample reviews later with real API data.
  const [reviews, setReviews] = useState([
    {
      id: "r1",
      course: "CMPS 271",
      professor: "Staff",
      text: "Good intro to product development. Workload is manageable if you start early.",
      likes: 12,
      dislikes: 1,
      createdAt: "2026-02-15",
    },
    {
      id: "r2",
      course: "CMPS 244",
      professor: "Staff",
      text: "SQL part is straightforward, but assignments need careful debugging.",
      likes: 7,
      dislikes: 0,
      createdAt: "2026-02-18",
    },
    {
      id: "r3",
      course: "CMPS 200",
      professor: "Staff",
      text: "Heavy theory. Great if you like proofs, otherwise it can feel rough.",
      likes: 4,
      dislikes: 3,
      createdAt: "2026-02-20",
    },
  ])

  // reaction per reviewId: "like" | "dislike" | null
  const [reactions, setReactions] = useState({})

  // Load saved reactions from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem("review_reactions")
      if (raw) setReactions(JSON.parse(raw))
    } catch {
      // ignore
    }
  }, [])

  // Persist reactions
  useEffect(() => {
    try {
      localStorage.setItem("review_reactions", JSON.stringify(reactions))
    } catch {
      // ignore
    }
  }, [reactions])

  const applyReaction = (reviewId, nextReaction) => {
    const prevReaction = reactions[reviewId] ?? null
    if (prevReaction === nextReaction) return

    // Update counts optimistically
    setReviews((prev) =>
      prev.map((r) => {
        if (r.id !== reviewId) return r

        let likes = r.likes
        let dislikes = r.dislikes

        // remove previous
        if (prevReaction === "like") likes -= 1
        if (prevReaction === "dislike") dislikes -= 1

        // add next
        if (nextReaction === "like") likes += 1
        if (nextReaction === "dislike") dislikes += 1

        return { ...r, likes, dislikes }
      })
    )

    setReactions((prev) => ({ ...prev, [reviewId]: nextReaction }))

    // Later: send to backend
    // await fetch(`/api/reviews/${reviewId}/reaction`, { method: "POST", ... })
  }

  const categories = [
    { id: "all", name: "All Courses" },
    { id: "computer-science", name: "Computer Science" },
    { id: "mathematics", name: "Mathematics" },
    { id: "engineering", name: "Engineering" },
    { id: "business", name: "Business" },
    { id: "science", name: "Science" },
  ]

  // Sample courses data
  const sampleCourses = [
    {
      id: 1,
      title: "Introduction to Python",
      category: "computer-science",
      instructor: "Dr. Smith",
      students: 245,
      rating: 4.8,
      image: "🐍",
    },
    {
      id: 2,
      title: "Data Structures",
      category: "computer-science",
      instructor: "Prof. Johnson",
      students: 189,
      rating: 4.7,
      image: "📊",
    },
    {
      id: 3,
      title: "Calculus I",
      category: "mathematics",
      instructor: "Dr. Brown",
      students: 312,
      rating: 4.6,
      image: "∫",
    },
    {
      id: 4,
      title: "Linear Algebra",
      category: "mathematics",
      instructor: "Prof. Davis",
      students: 156,
      rating: 4.9,
      image: "⚙️",
    },
    {
      id: 5,
      title: "Circuit Design",
      category: "engineering",
      instructor: "Dr. Wilson",
      students: 98,
      rating: 4.5,
      image: "⚡",
    },
    {
      id: 6,
      title: "Business Analytics",
     category: "business",
      instructor: "Prof. Miller",
      students: 203,
      rating: 4.7,
      image: "💼",
    },
    {
      id: 7,
      title: "Web Development",
      category: "computer-science",
      instructor: "Dr. Taylor",
      students: 421,
      rating: 4.8,
      image: "🌐",
    },
    {
      id: 8,
      title: "Chemistry Fundamentals",
      category: "science",
      instructor: "Prof. Anderson",
      students: 267,
      rating: 4.6,
      image: "⚗️",
    },
  ]

  useEffect(() => {
    setCourses(sampleCourses)
    setFilteredCourses(sampleCourses)
  }, [])

  useEffect(() => {
    let filtered = courses

    // Filter by category
    if (selectedCategory !== "all") {
      filtered = filtered.filter((course) => course.category === selectedCategory)
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(
        (course) =>
          course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          course.instructor.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    setFilteredCourses(filtered)
  }, [searchQuery, selectedCategory, courses])

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
          <h2>Categories</h2>
          <div className="categories-grid">
            {categories.map((category) => (
              <button
                key={category.id}
                className={`category-btn ${selectedCategory === category.id ? "active" : ""}`}
                onClick={() => setSelectedCategory(category.id)}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>

        {/* Courses Section */}
        <div className="courses-section">
          <h2>
            {selectedCategory === "all"
              ? "All Courses"
              : `${categories.find((c) => c.id === selectedCategory)?.name}`}
          </h2>

          <div className="courses-grid">
            {filteredCourses.length > 0 ? (
              filteredCourses.map((course) => (
                <div key={course.id} className="course-card">
                  <div className="course-image">{course.image}</div>
                  <div className="course-content">
                    <h3>{course.title}</h3>
                    <p className="instructor">👨‍🏫 {course.instructor}</p>
                    <div className="course-meta">
                      <span className="students">👥 {course.students} students</span>
                      <span className="rating">⭐ {course.rating}</span>
                    </div>
                    <button className="enroll-btn">Enroll Now</button>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-courses">
                <p>No courses found. Try adjusting your search or filter.</p>
              </div>
            )}
          </div>
        </div>

        {/* Reviews Section (Sprint 2: Like/Dislike) */}
        <div className="courses-section">
          <h2>Recent Reviews</h2>

          <div style={{ display: "grid", gap: "1rem" }}>
            {reviews
              .slice()
              .sort((a, b) => (b.likes - b.dislikes) - (a.likes - a.dislikes))
              .map((review) => (
                <ReviewCard
                  key={review.id}
                  review={review}
                  reaction={reactions[review.id] ?? null}
                  onReact={(next) => applyReaction(review.id, next)}
                />
              ))}
          </div>

          <p style={{ marginTop: "0.75rem", opacity: 0.8, fontSize: "0.9rem" }}>
            Your like/dislike choice is stored locally on this device.
          </p>
        </div>

        {/* Profile Section */}
        <div className="profile-card-section">
          <div className="profile-card">
            <h2>My Profile</h2>
            <div className="profile-info">
              <div className="profile-item">
                <label>Username:</label>
                <span>{user?.username || "N/A"}</span>
              </div>
              <div className="profile-item">
                <label>User ID:</label>
                <span>{user?.user_id || "N/A"}</span>
              </div>
              <div className="profile-item">
                <label>Role:</label>
                <span>{user?.role || "Student"}</span>
              </div>
              <div className="profile-item">
                <label>Email:</label>
                <span>{user?.email || "Not provided"}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Landing