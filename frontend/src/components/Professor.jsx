import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getProfessor, getProfessorReviews } from "../api";
import ProfessorReviewList from "./ProfessorReviewList";
import ProfessorReviewForm from "./ProfessorReviewForm";

export default function Professor() {
  const { id } = useParams();
  const [professor, setProfessor] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const profData = await getProfessor(id);
      const revData = await getProfessorReviews(id);
      setProfessor(profData);
      setReviews(revData);
      setLoading(false);
    };
    fetchData();
  }, [id]);

  if (loading) return <div>Loading professor...</div>;
  if (!professor) return <div>Professor not found</div>;

  return (
    <div>
      <h2>{professor.name}</h2>
      <p>Department: {professor.department}</p>

      <ProfessorReviewList reviews={reviews} />
      <ProfessorReviewForm professorId={id} onNewReview={(r) => setReviews([...reviews, r])} />
    </div>
  );
}
