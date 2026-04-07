// src/components/ReviewList.jsx
export default function ReviewList({ reviews }) {
  if (!reviews || reviews.length === 0) return <p>No reviews yet.</p>;

  return (
    <div>
      <h3>Reviews</h3>
      <ul>
        {reviews.map((r) => (
          <li key={r.id}>
            <strong>{r.user.name}:</strong> {r.comment} ({r.rating}/5)
          </li>
        ))}
      </ul>
    </div>
  );
}
