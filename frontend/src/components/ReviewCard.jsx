import React from "react"

/**
 * Shared review card component.
 * review: { id, course, professor, text, likes, dislikes, createdAt }
 * reaction: "like" | "dislike" | null
 * onReact: (nextReaction) => void   — called with null to remove reaction
 */
function ReviewCard({ review, reaction, onReact }) {
  const net = (review.likes ?? 0) - (review.dislikes ?? 0)

  const handleLike = () => onReact(reaction === "like" ? null : "like")
  const handleDislike = () => onReact(reaction === "dislike" ? null : "dislike")

  return (
    <div
      style={{
        background: "white",
        borderRadius: "12px",
        padding: "1.25rem 1.5rem",
        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
        textAlign: "left",
        transition: "transform 0.2s, box-shadow 0.2s",
      }}
    >
      {/* Header row */}
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <h3 style={{ margin: 0, color: "#111", fontSize: "1.05rem" }}>{review.course}</h3>
          <p style={{ margin: "0.2rem 0 0", color: "#666", fontSize: "0.875rem" }}>
            {review.professor}
            {review.createdAt ? ` · ${review.createdAt}` : ""}
          </p>
        </div>

        <div style={{ textAlign: "right", color: "#888", fontSize: "0.875rem" }}>
          <div style={{ fontWeight: 600, color: net >= 0 ? "#16a34a" : "#dc2626" }}>
            {net >= 0 ? "+" : ""}{net} net
          </div>
          <div>
            {review.likes} 👍 &nbsp; {review.dislikes} 👎
          </div>
        </div>
      </div>

      {/* Review text */}
      <p style={{ margin: "0.9rem 0", color: "#444", lineHeight: 1.6 }}>{review.text}</p>

      {/* Action buttons */}
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <button
          type="button"
          onClick={handleLike}
          aria-pressed={reaction === "like"}
          style={{
            padding: "0.45rem 0.9rem",
            borderRadius: "8px",
            border: "1px solid",
            borderColor: reaction === "like" ? "#16a34a" : "#d1d5db",
            background: reaction === "like" ? "#dcfce7" : "transparent",
            color: reaction === "like" ? "#16a34a" : "#555",
            cursor: "pointer",
            fontWeight: 500,
            fontSize: "0.875rem",
            transition: "all 0.15s",
          }}
        >
          👍 Like
        </button>

        <button
          type="button"
          onClick={handleDislike}
          aria-pressed={reaction === "dislike"}
          style={{
            padding: "0.45rem 0.9rem",
            borderRadius: "8px",
            border: "1px solid",
            borderColor: reaction === "dislike" ? "#dc2626" : "#d1d5db",
            background: reaction === "dislike" ? "#fee2e2" : "transparent",
            color: reaction === "dislike" ? "#dc2626" : "#555",
            cursor: "pointer",
            fontWeight: 500,
            fontSize: "0.875rem",
            transition: "all 0.15s",
          }}
        >
          👎 Dislike
        </button>

        {reaction && (
          <button
            type="button"
            onClick={() => onReact(null)}
            style={{
              marginLeft: "auto",
              padding: "0.45rem 0.9rem",
              borderRadius: "8px",
              border: "1px solid #d1d5db",
              background: "transparent",
              color: "#888",
              cursor: "pointer",
              fontSize: "0.875rem",
            }}
          >
            Clear
          </button>
        )}
      </div>
    </div>
  )
}

export default ReviewCard
