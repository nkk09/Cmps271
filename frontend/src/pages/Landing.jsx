import { useState, useEffect } from "react";
import "../styles/landing.css";
import api from "../api";

function Landing({ onViewCourseDetails, onViewProfessorReviews }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [professors, setProfessors] = useState([]);
  const [filteredProfessors, setFilteredProfessors] = useState([]);

  // Fetch courses and professors from backend or sample data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const coursesData = await api.courses.list({ limit: 100 });
        setCourses(coursesData || []);
        setFilteredCourses(coursesData || []);

        const professorsData = await api.professors.list({ limit: 100 });
        setProfessors(professorsData || []);
        setFilteredProfessors(professorsData || []);
      } catch (err) {
        console.error("Failed to load data:", err);
      }
    };
    fetchData();
  }, []);

  // Filter courses based on search & category
  useEffect(() => {
    let filtered = courses;
    if (searchQuery) {
      filtered = filtered.filter(
        (c) =>
          (c.title || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
          (c.code || "").toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    setFilteredCourses(filtered);

    // Filter professors by search query
    let profFiltered = professors;
    if (searchQuery) {
      profFiltered = profFiltered.filter((p) =>
        (`${p.first_name || ""} ${p.last_name || ""}`)
          .toLowerCase()
          .includes(searchQuery.toLowerCase()) ||
        (p.department || "").toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    setFilteredProfessors(profFiltered);
  }, [searchQuery, courses, professors]);

  return (
    <div className="landing-page">
      {/* Main Content */}
      <main className="landing-main">
        {/* Search Bar */}
        <div className="search-section">
          <input
            type="text"
            className="search-bar"
            placeholder="🔍 Search courses, professors, or instructors..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Courses */}
        <div className="courses-section">
          <h2>All Courses</h2>
          <div className="courses-grid">
            {filteredCourses.length > 0 ? (
              filteredCourses.map((course) => (
                <div key={course.id} className="course-card">
                  <div className="course-content">
                    <h3>{course.code} - {course.title}</h3>
                    <p className="instructor">🏛 {(course.code || "").split(" ")[0] || course.department}</p>
                    <div className="course-meta">
                      <span className="students">📚 Course</span>
                      <span className="rating">⭐ N/A</span>
                    </div>
                    <button className="enroll-btn" onClick={() => onViewCourseDetails?.(course.id)}>
                      View Details
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-courses">
                <p>No courses found.</p>
              </div>
            )}
          </div>
        </div>

        {/* Professors */}
        <div className="professors-section">
          <h2>Professors</h2>
          <div className="professors-grid">
            {filteredProfessors.length > 0 ? (
              filteredProfessors.map((prof) => (
                <div key={prof.id} className="professor-card">
                  <h3>{prof.first_name} {prof.last_name}</h3>
                  <p>🏛 {prof.department || "Department N/A"}</p>
                  <button className="view-btn" onClick={() => onViewProfessorReviews?.(prof.id)}>
                    View Reviews
                  </button>
                </div>
              ))
            ) : (
              <p>No professors found.</p>
            )}
          </div>
        </div>

        
      </main>
    </div>
  );
}

export default Landing;
