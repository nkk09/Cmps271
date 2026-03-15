import { useState, useEffect } from "react"
import "../styles/me.css"
import api from "../api"

function Me() {
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
  const major = userData?.student?.major || "Not set"

  return (
    <div className="me-page">
      <div className="me-container">
        {loading && <p>Loading...</p>}
        {error && <p className="error">{error}</p>}

        {userData && (
          <>
            <div className="me-card">
              <h1>Welcome, {username}!</h1>
              <div className="user-info">
                <p><strong>Anonymous Username:</strong> {username}</p>
                <p><strong>Role:</strong> {role}</p>
                <p><strong>Major:</strong> {major}</p>
                <p><strong>Member Since:</strong> {memberSince}</p>
              </div>
            </div>

            <div className="my-reviews-section">
              <h2>My Reviews ({myReviews.length})</h2>
              {myReviews.length === 0 ? (
                <p>You haven't written any reviews yet.</p>
              ) : (
                myReviews.map((review) => (
                  <div key={review.id} className="review-card">
                    <div className="review-header">
                      <span className="review-rating">⭐ {review.rating.toFixed(1)}/5</span>
                      <span className={`status-badge status-${review.status}`}>
                        {review.status}
                      </span>
                    </div>
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