import { useState, useEffect, useRef } from "react"
import "../styles/reviews.css"
import api from "../api"
import ReviewCard from "../components/ReviewCard"

/* ---------- Searchable Course Dropdown ---------- */
function CourseSearchSelect({ courses, value, onChange, placeholder = "Select a Course" }) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const ref = useRef(null)

  const selected = courses.find((c) => c.id === value)

  const filtered = query.trim()
    ? courses.filter(
        (c) =>
          c.code.toLowerCase().includes(query.toLowerCase()) ||
          c.title.toLowerCase().includes(query.toLowerCase())
      )
    : courses

  // Close on outside click
  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const handleSelect = (id) => {
    onChange(id)
    setQuery("")
    setOpen(false)
  }

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <div
        onClick={() => setOpen((o) => !o)}
        style={{
          padding: "0.55rem 0.85rem",
          border: "1px solid #d1d5db",
          borderRadius: "8px",
          background: "white",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "0.925rem",
          minWidth: "220px",
        }}
      >
        <span style={{ color: selected ? "#111" : "#999" }}>
          {selected ? `${selected.code} — ${selected.title}` : placeholder}
        </span>
        <span style={{ color: "#888", marginLeft: "0.5rem" }}>{open ? "▴" : "▾"}</span>
      </div>

      {open && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 4px)",
            left: 0,
            right: 0,
            background: "white",
            border: "1px solid #d1d5db",
            borderRadius: "8px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
            zIndex: 999,
            minWidth: "280px",
          }}
        >
          <div style={{ padding: "0.5rem" }}>
            <input
              autoFocus
              type="text"
              placeholder="Search courses..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              style={{
                width: "100%",
                padding: "0.45rem 0.7rem",
                border: "1px solid #d1d5db",
                borderRadius: "6px",
                fontSize: "0.875rem",
                boxSizing: "border-box",
              }}
            />
          </div>
          <div style={{ maxHeight: "240px", overflowY: "auto" }}>
            {value && (
              <div
                onClick={() => handleSelect("")}
                style={{
                  padding: "0.55rem 1rem",
                  cursor: "pointer",
                  fontSize: "0.875rem",
                  color: "#888",
                  borderBottom: "1px solid #f0f0f0",
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = "#f9fafb"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
              >
                — Clear selection
              </div>
            )}
            {filtered.length === 0 && (
              <div style={{ padding: "0.75rem 1rem", color: "#999", fontSize: "0.875rem" }}>No courses found</div>
            )}
            {filtered.map((course) => (
              <div
                key={course.id}
                onClick={() => handleSelect(course.id)}
                style={{
                  padding: "0.55rem 1rem",
                  cursor: "pointer",
                  fontSize: "0.875rem",
                  background: course.id === value ? "#eff6ff" : "transparent",
                  color: course.id === value ? "#2563eb" : "#111",
                }}
                onMouseEnter={(e) => { if (course.id !== value) e.currentTarget.style.background = "#f9fafb" }}
                onMouseLeave={(e) => { if (course.id !== value) e.currentTarget.style.background = "transparent" }}
              >
                <strong>{course.code}</strong> — {course.title}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

/* ---------- Main Reviews Page ---------- */
function Reviews({ user, initialCourseId = "", initialProfessorId = "", navigationToken = 0 }) {
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
  const [showReportForm, setShowReportForm] = useState(false)
  const [reportingReviewId, setReportingReviewId] = useState("")
  const [reportData, setReportData] = useState({
    violation_type: "other",
    severity: "medium",
    reason: "",
  })

  // Separate course selection for the create form
  const [formCourse, setFormCourse] = useState("")
  const [formSections, setFormSections] = useState([])
  const [loadingFormSections, setLoadingFormSections] = useState(false)

  const [formData, setFormData] = useState({
    section_id: "",
    content: "",
    rating: 5,
  })

  const isStudent = user?.roles?.includes("student")
  const studentId = user?.student?.id

  useEffect(() => {
    if (initialCourseId) {
      setSelectedCourse(initialCourseId)
      setSelectedProfessor("")
      return
    }
    if (initialProfessorId) {
      setSelectedProfessor(initialProfessorId)
      setSelectedCourse("")
    }
  }, [initialCourseId, initialProfessorId, navigationToken])

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

  // Load sections for the filter panel when course is selected
  useEffect(() => {
    if (!selectedCourse) { setSections([]); return }
    setLoadingSections(true)
    api.courses.getSections(selectedCourse)
      .then((data) => setSections(data || []))
      .catch(() => setSections([]))
      .finally(() => setLoadingSections(false))
  }, [selectedCourse])

  // Load sections for the CREATE form when formCourse changes
  useEffect(() => {
    if (!formCourse) { setFormSections([]); return }
    setLoadingFormSections(true)
    api.courses.getSections(formCourse)
      .then((data) => setFormSections(data || []))
      .catch(() => setFormSections([]))
      .finally(() => setLoadingFormSections(false))
  }, [formCourse])

  // Derive professors available for the selected course from sections
  const availableProfessors = selectedCourse
    ? Array.from(
        new Map(
          sections
            .filter((s) => s.professor)
            .map((s) => [s.professor.id, s.professor])
        ).values()
      )
    : professors

  // Load reviews whenever filters change
  useEffect(() => {
    if (!selectedCourse && !selectedProfessor) { setReviews([]); return }
    const loadReviews = async () => {
      setReviews([])
      try {
        let data = []
        if (selectedCourse) {
          const courseSections = sections.length ? sections : await api.courses.getSections(selectedCourse)
          const filtered = selectedProfessor
            ? courseSections.filter((s) => s.professor?.id === selectedProfessor)
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
  }, [selectedCourse, selectedProfessor, sortBy, sections])

  const reloadReviews = async (overrideCourse, overrideProfessor) => {
    const course = overrideCourse !== undefined ? overrideCourse : selectedCourse
    const professor = overrideProfessor !== undefined ? overrideProfessor : selectedProfessor
    if (!course && !professor) return
    try {
      let data = []
      if (course) {
        const courseSections = (course === selectedCourse && sections.length)
          ? sections
          : await api.courses.getSections(course)
        const filtered = professor
          ? courseSections.filter((s) => s.professor?.id === professor)
          : courseSections
        const allReviews = await Promise.all(
          filtered.map((s) => api.sections.getReviews(s.id, { sort_by: sortBy }).catch(() => []))
        )
        data = allReviews.flat()
      } else if (professor) {
        data = await api.professors.getReviews(professor, { sort_by: sortBy })
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
      const postedCourse = formCourse
      setFormData({ section_id: "", content: "", rating: 5 })
      setFormCourse("")
      setFormSections([])
      setShowCreateForm(false)
      setSelectedCourse(postedCourse)
      setSelectedProfessor("")
      await reloadReviews(postedCourse, "")
    } catch (err) {
      setError(err.message || "Failed to post review")
    } finally {
      setLoading(false)
    }
  }

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

  const handleEditReview = async (reviewId, newContent) => {
    try {
      await api.reviews.update(reviewId, { content: newContent })
      await reloadReviews()
    } catch (err) {
      setError(err.message || "Failed to update review")
    }
  }

  const openReportForm = (reviewId) => {
    setReportData({ violation_type: "other", severity: "medium", reason: "" })
    setReportingReviewId(reviewId)
    setShowReportForm(true)
  }

  const handleSubmitReport = async (e) => {
    e.preventDefault()
    if (!reportingReviewId) return

    setLoading(true)
    setError("")
    try {
      await api.violations.report(reportingReviewId, {
        violation_type: reportData.violation_type,
        severity: reportData.severity,
        reason: reportData.reason.trim() || undefined,
      })
      setShowReportForm(false)
      setReportingReviewId("")
      setReportData({ violation_type: "other", severity: "medium", reason: "" })
    } catch (err) {
      setError(err.message || "Failed to report this review")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="reviews-page">
      <div className="reviews-inner">
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

        {showReportForm && (
          <div className="report-overlay">
            <div className="report-modal">
              <h2>Report Review</h2>
              <form onSubmit={handleSubmitReport}>
                <div className="form-group">
                  <label>Violation Type</label>
                  <select
                    value={reportData.violation_type}
                    onChange={(e) => setReportData((r) => ({ ...r, violation_type: e.target.value }))}
                  >
                    <option value="spam">Spam</option>
                    <option value="harassment">Harassment</option>
                    <option value="hate_speech">Hate Speech</option>
                    <option value="misinformation">Misinformation</option>
                    <option value="personal_data">Personal Data</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Severity</label>
                  <select
                    value={reportData.severity}
                    onChange={(e) => setReportData((r) => ({ ...r, severity: e.target.value }))}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Reason (optional)</label>
                  <textarea
                    rows={4}
                    value={reportData.reason}
                    onChange={(e) => setReportData((r) => ({ ...r, reason: e.target.value }))}
                    placeholder="Add context for moderators..."
                  />
                </div>

                <div className="report-actions">
                  <button type="button" className="report-cancel" onClick={() => setShowReportForm(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="report-submit" disabled={loading}>
                    {loading ? "Submitting..." : "Submit Report"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Create Review Form */}
        {showCreateForm && isStudent && (
          <div className="create-review-form">
            <h2>Write a Review</h2>
            <form onSubmit={handleCreateReview}>
              <div className="form-group">
                <label>Course *</label>
                <CourseSearchSelect
                  courses={courses}
                  value={formCourse}
                  onChange={(id) => {
                    setFormCourse(id)
                    setFormData((f) => ({ ...f, section_id: "" }))
                  }}
                  placeholder="Search and select a course"
                />
              </div>

              <div className="form-group">
                <label>Section *</label>
                <select
                  value={formData.section_id}
                  onChange={(e) => setFormData((f) => ({ ...f, section_id: e.target.value }))}
                  required
                  disabled={!formCourse || loadingFormSections}
                >
                  <option value="">
                    {loadingFormSections ? "Loading sections..." : "Select a Section"}
                  </option>
                  {formSections.map((section) => (
                    <option key={section.id} value={section.id}>
                      {section.section_number} — {section.professor?.first_name} {section.professor?.last_name} — {section.semester?.name}
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
            <CourseSearchSelect
              courses={courses}
              value={selectedCourse}
              onChange={(id) => {
                setSelectedCourse(id)
                setSelectedProfessor("")
              }}
              placeholder="Select a Course"
            />
          </div>
          <div className="filter-group">
            <label>Filter by Professor</label>
            <select
              value={selectedProfessor}
              onChange={(e) => setSelectedProfessor(e.target.value)}
              disabled={selectedCourse && loadingSections}
            >
              <option value="">All Professors</option>
              {availableProfessors.map((prof) => (
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

        {/* Normal Reviews List */}
        <div className="reviews-list">
          {loading && <div className="loading">Loading reviews...</div>}

          {!loading && (selectedCourse || selectedProfessor) && reviews.length === 0 && (
            <div className="no-reviews">
              <p>No approved reviews yet. Be the first to write one!</p>
            </div>
          )}

          {reviews.map((review) => {
            const myInteraction = review.my_interaction ?? null
            const isMyReview = !!(studentId && review.student?.id === studentId)
            const courseCode = review.section?.course?.code || "Course"
            const profName = review.section?.professor
              ? `${review.section.professor.first_name} ${review.section.professor.last_name}`
              : "Professor"

            return (
              <ReviewCard
                key={review.id}
                review={{
                  id: review.id,
                  course: courseCode,
                  professor: profName,
                  text: review.content,
                  likes: review.likes_count,
                  dislikes: review.dislikes_count,
                  createdAt: new Date(review.created_at).toLocaleDateString(),
                }}
                reaction={myInteraction}
                onReact={(next) => handleInteract(review.id, next, myInteraction)}
                disableInteract={isMyReview}
                author={review.student?.username || "anonymous"}
                isMyReview={isMyReview}
                onDelete={isMyReview ? () => handleDeleteReview(review.id) : undefined}
                onEdit={isMyReview ? (newContent) => handleEditReview(review.id, newContent) : undefined}
                canReport={isStudent}
                onReport={() => openReportForm(review.id)}
              />
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default Reviews
