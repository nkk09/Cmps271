import React, { useState } from "react"

/**
 * Shared review card component.
 * review: { id, course, professor, text, likes, dislikes, createdAt }
 * reaction: "like" | "dislike" | null
 * onReact: (nextReaction) => void
 * author: string (username)
 * authorMajor: string | undefined
 * isMyReview: bool
 * onDelete: () => void
 * onEdit: (newContent) => void
 * canReport: bool
 * onReport: () => void
 */
function ReviewCard({
  review,
  userRole,
  reaction,
  onReact,
  disableInteract = false,
  author,
  authorMajor,
  isMyReview,
  onDelete,
  onEdit,
  canReport = false,
  onReport,
}) {
  const net = (review.likes ?? 0) - (review.dislikes ?? 0)
  const [editing, setEditing] = useState(false)
  const [editContent, setEditContent] = useState(review.text || "")

  const handleLike = () => { if (!disableInteract) onReact(reaction === "like" ? null : "like") }
  const handleDislike = () => { if (!disableInteract) onReact(reaction === "dislike" ? null : "dislike") }

  const handleSaveEdit = () => {
    if (editContent.trim().length < 20) return
    onEdit && onEdit(editContent.trim())
    setEditing(false)
  }

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
          {review.rating && (
            <div style={{ margin: "0.35rem 0 0", display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <span style={{ fontSize: "1rem" }}>
                {"⭐".repeat(Math.round(review.rating))}
              </span>
              <span style={{ fontSize: "0.85rem", color: "#f59e0b", fontWeight: 600 }}>
                {review.rating.toFixed(1)}/5
              </span>
            </div>
          )}
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

      {/* Review text or edit textarea */}
      {editing ? (
        <div style={{ margin: "0.9rem 0" }}>
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            rows={5}
            style={{
              width: "100%",
              padding: "0.6rem",
              borderRadius: "8px",
              border: "1px solid #d1d5db",
              fontSize: "0.925rem",
              lineHeight: 1.6,
              boxSizing: "border-box",
              resize: "vertical",
            }}
          />
          <small style={{ color: "#888" }}>{editContent.length} characters (min 20)</small>
        </div>
      ) : (
        <p style={{ margin: "0.9rem 0", color: "#444", lineHeight: 1.6 }}>{review.text}</p>
      )}

      {/* Action buttons */}
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
        {!editing && (
          <>
            <button
              type="button"
              onClick={handleLike}
              aria-pressed={reaction === "like"}
              disabled={disableInteract}
              title={disableInteract ? "You can't react to your own review" : ""}
              style={{
                padding: "0.45rem 0.9rem",
                borderRadius: "8px",
                border: "1px solid",
                borderColor: reaction === "like" ? "#16a34a" : "#d1d5db",
                background: reaction === "like" ? "#dcfce7" : "transparent",
                color: reaction === "like" ? "#16a34a" : "#555",
                cursor: disableInteract ? "not-allowed" : "pointer",
                fontWeight: 500,
                fontSize: "0.875rem",
                opacity: disableInteract ? 0.45 : 1,
                transition: "all 0.15s",
              }}
            >
              👍 Like
            </button>

            <button
              type="button"
              onClick={handleDislike}
              aria-pressed={reaction === "dislike"}
              disabled={disableInteract}
              title={disableInteract ? "You can't react to your own review" : ""}
              style={{
                padding: "0.45rem 0.9rem",
                borderRadius: "8px",
                border: "1px solid",
                borderColor: reaction === "dislike" ? "#dc2626" : "#d1d5db",
                background: reaction === "dislike" ? "#fee2e2" : "transparent",
                color: reaction === "dislike" ? "#dc2626" : "#555",
                cursor: disableInteract ? "not-allowed" : "pointer",
                fontWeight: 500,
                fontSize: "0.875rem",
                opacity: disableInteract ? 0.45 : 1,
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
          </>
        )}

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Author + owner actions */}
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
          {author && (
            <span style={{ fontSize: "0.8rem", color: "#888" }}>
              @{author}{authorMajor ? ` (${authorMajor})` : ""}
            </span>
          )}

          {isMyReview && onEdit && !editing && (
            <button
              type="button"
              onClick={() => { setEditContent(review.text || ""); setEditing(true) }}
              style={{
                background: "transparent",
                border: "1px solid rgba(59,130,246,0.4)",
                color: "#3b82f6",
                borderRadius: "8px",
                padding: "0.25rem 0.6rem",
                fontSize: "0.8rem",
                cursor: "pointer",
              }}
            >
              ✏️ Edit
            </button>
          )}

          {isMyReview && editing && (
            <>
              <button
                type="button"
                onClick={handleSaveEdit}
                disabled={editContent.trim().length < 20}
                style={{
                  background: "#3b82f6",
                  border: "none",
                  color: "white",
                  borderRadius: "8px",
                  padding: "0.25rem 0.7rem",
                  fontSize: "0.8rem",
                  cursor: editContent.trim().length < 20 ? "not-allowed" : "pointer",
                  opacity: editContent.trim().length < 20 ? 0.5 : 1,
                }}
              >
                Save
              </button>
              <button
                type="button"
                onClick={() => setEditing(false)}
                style={{
                  background: "transparent",
                  border: "1px solid #d1d5db",
                  color: "#555",
                  borderRadius: "8px",
                  padding: "0.25rem 0.6rem",
                  fontSize: "0.8rem",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
            </>
          )}

          {isMyReview && onDelete && !editing && (
            <button
              type="button"
              onClick={onDelete}
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

          {!isMyReview && canReport && onReport && !editing && (
            <button
              type="button"
              onClick={onReport}
              style={{
                background: "transparent",
                border: "1px solid rgba(217, 119, 6, 0.45)",
                color: "#b45309",
                borderRadius: "8px",
                padding: "0.25rem 0.6rem",
                fontSize: "0.8rem",
                cursor: "pointer",
              }}
            >
              🚩 Report
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ReviewCard
