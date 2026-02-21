import { useState, useEffect } from "react"
import "../styles/reviews.css"
import api from "../api"

function Reviews({ user }) {
  const [courses, setCourses] = useState([])
  const [professors, setProfessors] = useState([])
  const [reviews, setReviews] = useState([])
  const [sections, setSections] = useState([])
  
  const [selectedCourse, setSelectedCourse] = useState("")
  const [selectedProfessor, setSelectedProfessor] = useState("")
  const [selectedSection, setSelectedSection] = useState("")
  
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const [formData, setFormData] = useState({
    course_id: "",
    professor_id: "",
    section_id: "",
    title: "",
    content: "",
    rating: 5,
    attributes: "",
  })

  // Load initial data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [coursesData, professorsData, sectionsData] = await Promise.all([
          api.getCourses(),
          api.getProfessors(),
          api.getSections(),
        ])
        setCourses(coursesData || [])
        setProfessors(professorsData || [])
        setSections(sectionsData || [])
      } catch (err) {
        console.error("Failed to load data:", err)
        setError("Failed to load courses and professors")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Load reviews when filters change
  useEffect(() => {
    const loadReviews = async () => {
      try {
        const params = {}
        if (selectedCourse) params.course_id = selectedCourse
        if (selectedProfessor) params.professor_id = selectedProfessor
        if (selectedSection) params.section_id = selectedSection

        const reviewsData = await api.getReviews(params)
        setReviews(reviewsData.items || [])
      } catch (err) {
        console.error("Failed to load reviews:", err)
        setReviews([])
      }
    }

    loadReviews()
  }, [selectedCourse, selectedProfessor, selectedSection])

  const handleCreateReview = async (e) => {
    e.preventDefault()
    setError("")

    if (!formData.course_id || !formData.professor_id || !formData.title || !formData.content) {
      setError("Please fill in all required fields")
      return
    }

    setLoading(true)
    try {
      await api.createReview({
        course_id: parseInt(formData.course_id),
        professor_id: parseInt(formData.professor_id),
        section_id: formData.section_id ? parseInt(formData.section_id) : null,
        title: formData.title,
        content: formData.content,
        rating: parseFloat(formData.rating),
        attributes: formData.attributes || null,
      })

      // Reset form and reload reviews
      setFormData({
        course_id: "",
        professor_id: "",
        section_id: "",
        title: "",
        content: "",
        rating: 5,
        attributes: "",
      })
      setShowCreateForm(false)

      // Reload reviews
      const params = {}
      if (selectedCourse) params.course_id = selectedCourse
      if (selectedProfessor) params.professor_id = selectedProfessor
      const reviewsData = await api.getReviews(params)
      setReviews(reviewsData.items || [])
    } catch (err) {
      setError(err.message || "Failed to create review")
    } finally {
      setLoading(false)
    }
  }

  const handleLike = async (reviewId) => {
    try {
      await api.likeReview(reviewId)
      // Reload reviews
      const params = {}
      if (selectedCourse) params.course_id = selectedCourse
      const reviewsData = await api.getReviews(params)
      setReviews(reviewsData.items || [])
    } catch (err) {
      console.error("Failed to like review:", err)
    }
  }

  const handleDislike = async (reviewId) => {
    try {
      await api.dislikeReview(reviewId)
      // Reload reviews
      const params = {}
      if (selectedCourse) params.course_id = selectedCourse
      const reviewsData = await api.getReviews(params)
      setReviews(reviewsData.items || [])
    } catch (err) {
      console.error("Failed to dislike review:", err)
    }
  }

  return (
    <div className="reviews-page">
      <header className="reviews-header">
        <h1>📝 Course & Professor Reviews</h1>
        <button
          className="create-review-btn"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? "Cancel" : "Write a Review"}
        </button>
      </header>

      {error && <div className="error-message">{error}</div>}

      {/* Create Review Form */}
      {showCreateForm && (
        <div className="create-review-form">
          <h2>Write a Review</h2>
          <form onSubmit={handleCreateReview}>
            <div className="form-group">
              <label>Course *</label>
              <select
                value={formData.course_id}
                onChange={(e) => setFormData({ ...formData, course_id: e.target.value })}
                required
              >
                <option value="">Select a Course</option>
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.course_number} - {course.course_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Professor *</label>
              <select
                value={formData.professor_id}
                onChange={(e) => setFormData({ ...formData, professor_id: e.target.value })}
                required
              >
                <option value="">Select a Professor</option>
                {professors.map((prof) => (
                  <option key={prof.id} value={prof.id}>
                    {prof.first_name} {prof.last_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Section (Optional)</label>
              <select
                value={formData.section_id}
                onChange={(e) => setFormData({ ...formData, section_id: e.target.value })}
              >
                <option value="">Select a Section</option>
                {sections.map((section) => (
                  <option key={section.id} value={section.id}>
                    {section.section_number} - {section.semester}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g., Great course, learned a lot"
                required
                minLength="5"
              />
            </div>

            <div className="form-group">
              <label>Review *</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                placeholder="Share your thoughts about the course and professor..."
                required
                minLength="10"
              />
            </div>

            <div className="form-group">
              <label>Rating *</label>
              <select
                value={formData.rating}
                onChange={(e) => setFormData({ ...formData, rating: e.target.value })}
              >
                <option value="1">1 - Poor</option>
                <option value="2">2 - Fair</option>
                <option value="3">3 - Good</option>
                <option value="4">4 - Very Good</option>
                <option value="5">5 - Excellent</option>
              </select>
            </div>

            <div className="form-group">
              <label>Tags (comma-separated, optional)</label>
              <input
                type="text"
                value={formData.attributes}
                onChange={(e) => setFormData({ ...formData, attributes: e.target.value })}
                placeholder="e.g., difficulty, workload, teaching_style"
              />
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
            <option value="">All Courses</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.course_number} - {course.course_name}
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
      </div>

      {/* Reviews List */}
      <div className="reviews-list">
        {loading && <div className="loading">Loading reviews...</div>}
        {!loading && reviews.length === 0 && (
          <div className="no-reviews">
            <p>No reviews found. Be the first to write one!</p>
          </div>
        )}
        {!loading &&
          reviews.map((review) => (
            <div key={review.id} className="review-card">
              <div className="review-header">
                <div className="review-title">
                  <h3>{review.title}</h3>
                  <p className="reviewer">by {review.reviewer_username}</p>
                </div>
                <div className="review-rating">⭐ {review.rating}/5</div>
              </div>

              <div className="review-course-info">
                <span>
                  {review.course_number} - {review.professor_name}
                </span>
              </div>

              <p className="review-content">{review.content}</p>

              {review.attributes && (
                <div className="review-tags">
                  {review.attributes.split(",").map((tag) => (
                    <span key={tag} className="tag">
                      {tag.trim()}
                    </span>
                  ))}
                </div>
              )}

              <div className="review-interactions">
                <button
                  className="like-btn"
                  onClick={() => handleLike(review.id)}
                >
                  👍 {review.likes_count}
                </button>
                <button
                  className="dislike-btn"
                  onClick={() => handleDislike(review.id)}
                >
                  👎 {review.dislikes_count}
                </button>
                <span className="net-rating">Net: {review.net_rating}</span>
              </div>

              <p className="review-date">
                Posted {new Date(review.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
      </div>
    </div>
  )
}

export default Reviews
