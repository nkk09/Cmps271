import { useState, useEffect } from "react"
import "../styles/reviews.css"
import api from "../api"
import ReviewCard from "../components/ReviewCard"

function Reviews({ user }) {
  const [courses, setCourses] = useState([])
  const [professors, setProfessors] = useState([])
  const [reviews, setReviews] = useState([])
  const [sections, setSections] = useState([])
  const [loadingSections, setLoadingSections] = useState(false)
  const [selectedCourse, setSelectedCourse] = useState("")
  const [selectedProfessor, setSelectedProfessor] = useState("")
  const [sortBy, setSortBy] = useState("newest")
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const [formData, setFormData] = useState({
    section_id: "",
    content: "",
    rating: 5,
  })

  const isStudent = user?.roles?.includes("student")
  const studentId = user?.student?.id

  // Load courses and professors once
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [coursesData, professorsData] = await Promise.all([
          api.courses.list({ limit: 100 }),
          api.professors.list({ limit: 100 }),
        ])
        setCourses(coursesData || [])
        setProfessors(professorsData || [])
      } catch (err) {
        setError("Failed to load courses and professors")
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // Load sections when course is selected (for the create form)
  useEffect(() => {
    if (!selectedCourse) return
    setLoadingSections(true)
    api.courses.getSections(selectedCourse)
      .then((data) => setSections(data || []))
      .catch(() => setSections([]))
      .finally(() => setLoadingSections(false))
  }, [selectedCourse])

  // Load reviews whenever filters change
  useEffect(() => {
    if (!selectedCourse && !selectedProfessor) {
      setReviews([])
      return
    }
    const loadReviews = async () => {
      setReviews([])
      try {
        let data = []
        if (selectedCourse) {
          const courseSections = await api.courses.getSections(selectedCourse)
          const filtered = selectedProfessor
            ? courseSections.filter((s) => s.professor.id === selectedProfessor)
            : courseSections
          const allReviews = await Promise.all(
            filtered.map((s) =>
              api.sections.getReviews(s.id, { sort_by: sortBy }).catch(() => [])
            )
          )
          data = allReviews.flat()
        } else if (selectedProfessor) {
          data = await api.professors.getReviews(selectedProfessor, { sort_by: sortBy })
        }
        setReviews(data || [])
      } catch (err) {
        console.error("Failed to load reviews:", err)
        setReviews([])
      }
    }
    loadReviews()
  }, [selectedCourse, selectedProfessor, sortBy])

  const reloadReviews = async () => {
    if (!selectedCourse && !selectedProfessor) return
    try {
      let data = []
      if (selectedCourse) {
        const courseSections = await api.courses.getSections(selectedCourse)
        const filtered = selectedProfessor
          ? courseSections.filter((s) => s.professor.id === selectedProfessor)
          : courseSections
        const allReviews = await Promise.all(
          filtered.map((s) => api.sections.getReviews(s.id, { sort_by: sortBy }).catch(() => []))
        )
        data = allReviews.flat()
      } else if (selectedProfessor) {
        data = await api.professors.getReviews(selectedProfessor, { sort_by: sortBy })
      }
      setReviews(data || [])
    } catch (err) {
      console.error("Failed to reload reviews:", err)
    }
  }

  const handleCreateReview = async (e) => {
    e.preventDefault()
    setError("")
    if (!formData.section_id) { setError("Please select a section to review"); return }
    if (!formData.content || formData.content.length < 20) { setError("Review must be at least 20 characters"); return }

    setLoading(true)
    try {
      await api.sections.createReview(formData.section_id, {
        content: formData.content,
        rating: parseFloat(formData.rating),
      })
      setFormData({ section_id: "", content: "", rating: 5 })
      setShowCreateForm(false)
      await reloadReviews()
    } catch (err) {
      setError(err.message || "Failed to post review")
    } finally {
      setLoading(false)
    }
  }

  // Handles like/dislike from ReviewCard — toggles if same, removes if null
  const handleInteract = async (reviewId, next, current) => {
    try {
      if (current === next || next === null) {
        await api.reviews.removeInteraction(reviewId)
      } else if (next === "like") {
        await api.reviews.like(reviewId)
      } else {
        await api.reviews.dislike(reviewId)
      }
      await reloadReviews()
    } catch (err) {
      console.error("Interaction failed:", err)
    }
  }

  const handleDeleteReview = async (reviewId) => {
    if (!confirm("Delete this review?")) return
    try {
      await api.reviews.delete(reviewId)
      await reloadReviews()
    } catch (err) {
      setError(err.message || "Failed to delete review")
    }
  }

  return (
    <div className="reviews-page">
      <header className="reviews-header">
        <h1>📝 Course &amp; Professor Reviews</h1>
        {isStudent && (
          <button
            className="create-review-btn"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? "Cancel" : "Write a Review"}
          </button>
        )}
      </header>

      {error && <div className="error-message">{error}</div>}

      {/* Create Review Form */}
      {showCreateForm && isStudent && (
        <div className="create-review-form">
          <h2>Write a Review</h2>
          <form onSubmit={handleCreateReview}>
            <div className="form-group">
              <label>Course *</label>
              <select
                value={selectedCourse}
                onChange={(e) => {
                  setSelectedCourse(e.target.value)
                  setFormData((f) => ({ ...f, section_id: "" }))
                  setSections([])
                }}
                required
              >
                <option value="">Select a Course</option>
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.code} — {course.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Section *</label>
              <select
                value={formData.section_id}
                onChange={(e) => setFormData((f) => ({ ...f, section_id: e.target.value }))}
                required
                disabled={!selectedCourse || loadingSections}
              >
                <option value="">
                  {loadingSections ? "Loading sections..." : "Select a Section"}
                </option>
                {sections.map((section) => (
                  <option key={section.id} value={section.id}>
                    {section.section_number} — {section.professor.first_name} {section.professor.last_name} — {section.semester.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Review * (min. 20 characters)</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData((f) => ({ ...f, content: e.target.value }))}
                placeholder="Share your experience with the course and professor..."
                required
                minLength={20}
                rows={5}
              />
              <small>{formData.content.length} characters</small>
            </div>

            <div className="form-group">
              <label>Rating *</label>
              <select
                value={formData.rating}
                onChange={(e) => setFormData((f) => ({ ...f, rating: e.target.value }))}
              >
                <option value="1">1 — Poor</option>
                <option value="2">2 — Fair</option>
                <option value="3">3 — Good</option>
                <option value="4">4 — Very Good</option>
                <option value="5">5 — Excellent</option>
              </select>
            </div>

            <button type="submit" disabled={loading}>
              {loading ? "Posting..." : "Post Review"}
            </button>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="reviews-filters">
        <div className="filter-group">
          <label>Filter by Course</label>
          <select value={selectedCourse} onChange={(e) => setSelectedCourse(e.target.value)}>
            <option value="">Select a Course</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.code} — {course.title}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>Filter by Professor</label>
          <select value={selectedProfessor} onChange={(e) => setSelectedProfessor(e.target.value)}>
            <option value="">All Professors</option>
            {professors.map((prof) => (
              <option key={prof.id} value={prof.id}>
                {prof.first_name} {prof.last_name}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>Sort By</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="newest">Newest</option>
            <option value="top_rated">Top Rated</option>
            <option value="most_liked">Most Liked</option>
          </select>
        </div>
      </div>

      {!selectedCourse && !selectedProfessor && (
        <div className="no-reviews">
          <p>Select a course or professor above to see reviews.</p>
        </div>
      )}

      {/* Reviews List — rendered with the shared ReviewCard component */}
      <div className="reviews-list">
        {loading && <div className="loading">Loading reviews...</div>}

        {!loading && (selectedCourse || selectedProfessor) && reviews.length === 0 && (
          <div className="no-reviews">
            <p>No approved reviews yet. Be the first to write one!</p>
          </div>
        )}

        {reviews.map((review) => {
          const myInteraction = review.my_interaction ?? null
          const isMyReview = studentId && review.student?.id === studentId

          return (
            <div key={review.id}>
              <ReviewCard
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
              />

              {/* Extra metadata row below the card */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "-0.5rem", marginBottom: "0.5rem", padding: "0 0.25rem" }}>
                <span style={{ fontSize: "0.8rem", opacity: 0.7 }}>
                  @{review.student?.username || "anonymous"}
                  {review.status === "pending" && (
                    <span style={{ marginLeft: "0.5rem", color: "#f59e0b", fontWeight: 600 }}>· Pending approval</span>
                  )}
                </span>
                {isMyReview && (
                  <button
                    onClick={() => handleDeleteReview(review.id)}
                    style={{
                      background: "transparent",
                      border: "1px solid rgba(255,80,80,0.4)",
                      color: "#ef4444",
                      borderRadius: "8px",
                      padding: "0.25rem 0.6rem",
                      fontSize: "0.8rem",
                      cursor: "pointer",
                    }}
                  >
                    🗑 Delete
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default Reviews
