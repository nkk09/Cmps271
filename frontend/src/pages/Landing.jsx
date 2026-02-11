import { useState, useEffect } from "react"
import "../styles/landing.css"

function Landing({ user, onLogout }) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [courses, setCourses] = useState([])
  const [filteredCourses, setFilteredCourses] = useState([])

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
            {selectedCategory === "all" ? "All Courses" : `${categories.find((c) => c.id === selectedCategory)?.name}`}
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
