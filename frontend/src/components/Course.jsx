// src/components/Course.jsx
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getCourse, getReviews } from "../api";
import ReviewList from "./ReviewList";
import ReviewForm from "./ReviewForm";

export default function Course() {
  const { id } = useParams();       // course ID from URL
  const [course, setCourse] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const courseData = await getCourse(id);
        const reviewsData = await getReviews(id);
        setCourse(courseData);
        setReviews(reviewsData);
      } catch (err) {
        console.error("Failed to load course or reviews:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) return <div>Loading course...</div>;
  if (!course) return <div>Course not found</div>;

  return (
    <div>
      <h2>{course.name}</h2>
      <p>Professor: {course.professor}</p>

      <ReviewList reviews={reviews} />
      {/* ReviewForm will update the review list when a new review is submitted */}
      <ReviewForm courseId={id} onNewReview={(r) => setReviews([...reviews, r])} />
    </div>
  );
}
/* 
Consider optimistic updates and backend error handling for new reviews.
Could add average rating display here.
*/