import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getProfessors } from "../api";

export default function ProfessorList() {
  const [professors, setProfessors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfessors = async () => {
      const data = await getProfessors();
      setProfessors(data);
      setLoading(false);
    };
    fetchProfessors();
  }, []);

  if (loading) return <div>Loading professors...</div>;

  return (
    <div>
      <h2>Professors</h2>
      <ul>
        {professors.map((p) => (
          <li key={p.id}>
            <Link to={`/professors/${p.id}`}>{p.name} - {p.department}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
