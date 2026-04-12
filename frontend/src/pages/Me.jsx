import { useState, useEffect } from "react"
import "../styles/me.css"
import api from "../api"

function Me({ onLogout }) {
  const [userData, setUserData] = useState(null)
  const [myReviews, setMyReviews] = useState([])
  const [resolvedViolations, setResolvedViolations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState("")

  const formatLabel = (text) => {
    if (!text) return ""
    return text
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase())
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [me, reviews] = await Promise.all([
          api.users.getMe(),
          api.users.getMyReviews(),
        ])

        setUserData(me)
        setMyReviews(reviews || [])

        try {
          const violations = await api.violations.list({
            status_filter: "resolved",
            limit: 100,
          })
          const studentId = me?.student?.id
          const visibleViolations = (violations || []).filter((violation) => {
            if (!violation || violation.status !== "resolved") return false
            return studentId && violation.review?.student?.id === studentId
          })
          setResolvedViolations(visibleViolations)
        } catch (violationErr) {
          console.warn("Unable to fetch violations for profile page:", violationErr)
          setResolvedViolations([])
        }
      } catch (err) {
        console.error("Error fetching user:", err)
        setError("Failed to load profile")
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleLogout = async () => {
    await api.auth.logout()
    if (onLogout) onLogout()
  }

  const handleDeleteReview = async (reviewId) => {
    if (!confirm("Delete this review?")) return
    try {
      await api.reviews.delete(reviewId)
      setMyReviews((prev) => prev.filter((r) => r.id !== reviewId))
    } catch (err) {
      setError(err.message || "Failed to delete review")
    }
  }

  const username = userData?.student?.username || "N/A"
  const role = userData?.roles?.[0] || "student"
  const memberSince = userData?.user?.created_at
    ? new Date(userData.user.created_at).toLocaleDateString()
    : "N/A"
  const major = userData?.student?.major || ""

  const [editMajor, setEditMajor] = useState(major)

  useEffect(() => {
    setEditMajor(userData?.student?.major || "")
  }, [userData])

  return (
    <div className="me-page">
      <div className="me-container">
        {loading && <p>Loading...</p>}
        {error && <p className="error">{error}</p>}
        {message && <p className="success">{message}</p>}

        {userData && (
          <>
            <div className="me-card">
              <h1>My Profile</h1>
              <div className="user-info">
                <div className="info-item">
                  <label>Anonymous Username</label>
                  <span>{username}</span>
                </div>

                <div className="info-item">
                  <label>Role</label>
                  <span>{formatLabel(role)}</span>
                </div>

                <div className="info-item">
                  <label>Major</label>
                  <input
                    type="text"
                    value={editMajor}
                    onChange={(e) => setEditMajor(e.target.value)}
                    placeholder="Enter major"
                    className="major-input"
                    disabled={saving}
                  />
                </div>

                <div className="info-item">
                  <label>Member Since</label>
                  <span>{memberSince}</span>
                </div>
              </div>

              <button
                className="save-btn"
                onClick={async () => {
                  console.log("attempting to save major", editMajor, major)
                  setSaving(true)
                  setError("")
                  setMessage("")

                  try {
                    const updated = await api.users.updateMe({ major: editMajor })
                    setUserData((prev) => ({ ...prev, student: updated }))
                    setEditMajor(updated.major || "")

                    try {
                      const fresh = await api.users.getMe()
                      setUserData(fresh)
                    } catch (e) {
                      console.warn("could not refresh profile", e)
                    }

                    setMessage("Major saved successfully")
                    console.log("major saved", updated)
                  } catch (err) {
                    console.error("Failed to update major", err)
                    setError(err.message || "Could not save major")
                  } finally {
                    setSaving(false)
                  }
                }}
                disabled={saving}
              >
                {saving ? "Saving..." : "Save Major"}
              </button>
            </div>

            <div className="violations-section">
              <h2>Previous Violations</h2>
              {resolvedViolations.length === 0 ? (
                <div className="violations-card">
                  <p className="no-violations">No resolved violations recorded</p>
                </div>
              ) : (
                resolvedViolations.map((violation) => (
                  <div key={violation.id} className="violations-card">
                    <div className="violation-card-grid">
                      <div className="violation-meta-group">
                        <span className="violation-meta-label">Case ID</span>
                        <span className="violation-meta-value">{violation.id}</span>
                      </div>
                      <div className="violation-meta-group">
                        <span className="violation-meta-label">Review ID</span>
                        <span className="violation-meta-value">{violation.review_id}</span>
                      </div>
                      <div className="violation-meta-group">
                        <span className="violation-meta-label">Type</span>
                        <span className="violation-meta-value">{formatLabel(violation.violation_type)}</span>
                      </div>
                      <div className={`violation-meta-group severity-${violation.severity}`}>
                        <span className="violation-meta-label">Severity</span>
                        <span className="violation-meta-value">{formatLabel(violation.severity)}</span>
                      </div>
                      <div className="violation-meta-group">
                        <span className="violation-meta-label">Status</span>
                        <span className="violation-meta-value">{formatLabel(violation.status)}</span>
                      </div>
                      <div className="violation-meta-group">
                        <span className="violation-meta-label">Reported</span>
                        <span className="violation-meta-value">{new Date(violation.created_at).toLocaleString()}</span>
                      </div>
                      <div className="violation-meta-group">
                        <span className="violation-meta-label">Resolved</span>
                        <span className="violation-meta-value">
                          {violation.resolved_at
                            ? new Date(violation.resolved_at).toLocaleString()
                            : "Unknown"}
                        </span>
                      </div>
                    </div>

                    {violation.review?.content && (
                      <div className="violation-detail">
                        <p><strong>Reported Review</strong></p>
                        <p>{violation.review.content}</p>
                      </div>
                    )}

                    {violation.admin_notes && (
                      <div className="violation-detail">
                        <p><strong>Admin Notes</strong></p>
                        <p>{violation.admin_notes}</p>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="my-reviews-section">
              <h2>Recent Reviews ({myReviews.length})</h2>
              {myReviews.length === 0 ? (
                <p className="no-reviews">You haven't written any reviews yet.</p>
              ) : (
                myReviews.map((review) => (
                  <div key={review.id} className="review-card">
                    <div className="review-header">
                      <span className="review-rating">⭐ {review.rating.toFixed(1)}/5</span>
                      <span className={`status-badge status-${review.status}`}>
                        {formatLabel(review.status)}
                      </span>
                    </div>

                    {review.section?.course && (
                      <div className="review-course">
                        <strong>Course:</strong> {review.section.course.code} — {review.section.course.title}
                      </div>
                    )}

                    <p className="review-content">{review.content}</p>

                    <div className="review-footer">
                      <span>{new Date(review.created_at).toLocaleDateString()}</span>
                      <button
                        className="delete-btn"
                        onClick={() => handleDeleteReview(review.id)}
                      >
                        🗑 Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default Me