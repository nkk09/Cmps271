import React, { useState } from "react";
import { createProfessorReview } from "../api";

export default function ProfessorReviewForm({ professorId, onNewReview }) {
  const [comment, setComment] = useState("");
  const [rating, setRating] = useState(5);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const newReview = await createProfessorReview(professorId, { comment, rating });
    onNewReview(newReview);
    setComment("");
    setRating(5);
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <h4>Leave a review</h4>
      <textarea value={comment} onChange={(e) => setComment(e.target.value)} required />
      <br />
      <label>
        Rating:
        <select value={rating} onChange={(e) => setRating(Number(e.target.value))}>
          {[1, 2, 3, 4, 5].map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </label>
      <br />
      <button type="submit" disabled={loading}>{loading ? "Submitting..." : "Submit"}</button>
    </form>
  );
}
