import React from "react"

/**
 * review: { id, course, professor, text, likes, dislikes, createdAt }
 * reaction: "like" | "dislike" | null
 * onReact: (nextReaction) => void
 */
function ReviewCard({ review, reaction, onReact }) {
  const net = (review.likes ?? 0) - (review.dislikes ?? 0)

  const handleLike = () => {
    onReact(reaction === "like" ? null : "like")
  }

  const handleDislike = () => {
    onReact(reaction === "dislike" ? null : "dislike")
  }

  return (
    <div
      className="course-card"
      style={{
        textAlign: "left",
        padding: "1rem",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem" }}>
        <div>
          <h3 style={{ margin: 0 }}>{review.course}</h3>
          <p style={{ margin: "0.25rem 0 0", opacity: 0.85 }}>
            {review.professor}
            {review.createdAt ? ` • ${review.createdAt}` : ""}
          </p>
        </div>

        <div style={{ textAlign: "right", opacity: 0.85 }}>
          <div style={{ fontSize: "0.9rem" }}>Score: {net}</div>
          <div style={{ fontSize: "0.85rem" }}>
            {review.likes} 👍 / {review.dislikes} 👎
          </div>
        </div>
      </div>

      <p style={{ marginTop: "0.75rem", marginBottom: "0.75rem" }}>{review.text}</p>

      <div style={{ display: "flex", gap: "0.5rem" }}>
        <button
          type="button"
          onClick={handleLike}
          style={{
            padding: "0.5rem 0.75rem",
            borderRadius: "10px",
            border: "1px solid rgba(255,255,255,0.15)",
            background: reaction === "like" ? "rgba(255,255,255,0.12)" : "transparent",
            cursor: "pointer",
          }}
          aria-pressed={reaction === "like"}
        >
          👍 Like
        </button>

        <button
          type="button"
          onClick={handleDislike}
          style={{
            padding: "0.5rem 0.75rem",
            borderRadius: "10px",
            border: "1px solid rgba(255,255,255,0.15)",
            background: reaction === "dislike" ? "rgba(255,255,255,0.12)" : "transparent",
            cursor: "pointer",
          }}
          aria-pressed={reaction === "dislike"}
        >
          👎 Dislike
        </button>

        <button
          type="button"
          onClick={() => onReact(null)}
          disabled={!reaction}
          style={{
            marginLeft: "auto",
            padding: "0.5rem 0.75rem",
            borderRadius: "10px",
            border: "1px solid rgba(255,255,255,0.15)",
            background: "transparent",
            opacity: reaction ? 1 : 0.5,
            cursor: reaction ? "pointer" : "not-allowed",
          }}
        >
          Clear
        </button>
      </div>
    </div>
  )
}

export default ReviewCard