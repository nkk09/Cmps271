import { useState, useEffect } from "react"
import "../styles/me.css"
import api from "../api"

function Me({ onLogout }) {
  const [userData, setUserData] = useState(null)
  const [myReviews, setMyReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [me, reviews] = await Promise.all([
          api.users.getMe(),
          api.users.getMyReviews(),
        ])
        setUserData(me)
        setMyReviews(reviews || [])
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

  // /users/me returns { user, student, professor, roles }
  const username = userData?.student?.username || "N/A"
  const role = userData?.roles?.[0] || "student"
  const memberSince = userData?.user?.created_at
    ? new Date(userData.user.created_at).toLocaleDateString()
    : "N/A"
  const major = userData?.student?.major || ""

  const [editMajor, setEditMajor] = useState(major)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState("")

  // whenever userData loads or changes, keep the input in sync
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
                  <span>{role}</span>
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
              <button className="logout-btn" onClick={handleLogout}>
                🚪 Logout
              </button>
              <button
                className="save-btn"
                onClick={async () => {
                    console.log("attempting to save major", editMajor, major)
                  setSaving(true)
                  try {
                    const updated = await api.users.updateMe({ major: editMajor })
                      setUserData((prev) => ({ ...prev, student: updated }))
                    setEditMajor(updated.major || "")
                    // refresh from server to ensure persistence
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
              <div className="violations-card">
                <p className="no-violations">No violations recorded</p>
              </div>
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
                        {review.status}
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