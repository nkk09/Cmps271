import { useState, useEffect, useRef } from "react";
import "../styles/landing.css";
import api from "../api";

function Landing({ onViewCourseDetails, onViewProfessorReviews }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [professors, setProfessors] = useState([]);
  const [filteredProfessors, setFilteredProfessors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [coursesPage, setCoursesPage] = useState(1);
  const [professorsPage, setProfessorsPage] = useState(1);
  const [courseColumns, setCourseColumns] = useState(1);
  const [professorColumns, setProfessorColumns] = useState(1);

  const coursesGridRef = useRef(null);
  const professorsGridRef = useRef(null);

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
        } finally {
          setLoading(false);
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

  useEffect(() => {
    setCoursesPage(1);
    setProfessorsPage(1);
  }, [searchQuery]);

  useEffect(() => {
    const getGridColumns = (el) => {
      if (!el) return 1;
      const cols = window.getComputedStyle(el).gridTemplateColumns.split(" ").filter(Boolean).length;
      return Math.max(1, cols);
    };

    const updateColumns = () => {
      setCourseColumns(getGridColumns(coursesGridRef.current));
      setProfessorColumns(getGridColumns(professorsGridRef.current));
    };

    updateColumns();
    const observer = new ResizeObserver(updateColumns);
    if (coursesGridRef.current) observer.observe(coursesGridRef.current);
    if (professorsGridRef.current) observer.observe(professorsGridRef.current);
    window.addEventListener("resize", updateColumns);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", updateColumns);
    };
  }, []);

  const coursesPerPage = Math.max(1, courseColumns * 2);
  const professorsPerPage = Math.max(1, professorColumns * 2);

  const totalCoursePages = Math.max(1, Math.ceil(filteredCourses.length / coursesPerPage));
  const totalProfessorPages = Math.max(1, Math.ceil(filteredProfessors.length / professorsPerPage));

  const safeCoursesPage = Math.min(coursesPage, totalCoursePages);
  const safeProfessorsPage = Math.min(professorsPage, totalProfessorPages);

  const visibleCourses = filteredCourses.slice(
    (safeCoursesPage - 1) * coursesPerPage,
    safeCoursesPage * coursesPerPage
  );

  const visibleProfessors = filteredProfessors.slice(
    (safeProfessorsPage - 1) * professorsPerPage,
    safeProfessorsPage * professorsPerPage
  );

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
          <div className="courses-grid" ref={coursesGridRef}>
            {loading ? (
              <div className="no-courses"><p>Loading courses...</p></div>
            ) : visibleCourses.length > 0 ? (
              visibleCourses.map((course) => (
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
          {!loading && totalCoursePages > 1 && (
            <div className="pagination">
              {Array.from({ length: totalCoursePages }, (_, i) => i + 1).map((page) => (
                <button
                  key={`course-page-${page}`}
                  className={`page-btn ${safeCoursesPage === page ? "active" : ""}`}
                  onClick={() => setCoursesPage(page)}
                  type="button"
                >
                  {page}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Professors */}
        <div className="professors-section">
          <h2>Professors</h2>
          <div className="professors-grid" ref={professorsGridRef}>
            {loading ? (
              <div className="no-courses"><p>Loading professors...</p></div>
            ) : visibleProfessors.length > 0 ? (
              visibleProfessors.map((prof) => (
                <div key={prof.id} className="professor-card">
                  <h3>{prof.first_name} {prof.last_name}</h3>
                  <p>🏛 {prof.department || "Department N/A"}</p>
                  <button className="view-btn" onClick={() => onViewProfessorReviews?.(prof.id)}>
                    View Reviews
                  </button>
                </div>
              ))
            ) : (
              <div className="no-courses"><p>No professors found.</p></div>
            )}
          </div>
          {!loading && totalProfessorPages > 1 && (
            <div className="pagination">
              {Array.from({ length: totalProfessorPages }, (_, i) => i + 1).map((page) => (
                <button
                  key={`prof-page-${page}`}
                  className={`page-btn ${safeProfessorsPage === page ? "active" : ""}`}
                  onClick={() => setProfessorsPage(page)}
                  type="button"
                >
                  {page}
                </button>
              ))}
            </div>
          )}
        </div>

        
      </main>
    </div>
  );
}

export default Landing;
