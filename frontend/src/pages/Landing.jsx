import { useState, useEffect } from "react";
import "../styles/landing.css";
import { Link } from "react-router-dom";
import { getCourses, getProfessors } from "../api";

function Landing({ user, onLogout }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [professors, setProfessors] = useState([]);
  const [filteredProfessors, setFilteredProfessors] = useState([]);

  const categories = [
    { id: "all", name: "All Courses" },
    { id: "computer-science", name: "Computer Science" },
    { id: "mathematics", name: "Mathematics" },
    { id: "engineering", name: "Engineering" },
    { id: "business", name: "Business" },
    { id: "science", name: "Science" },
  ];

  // Fetch courses and professors from backend or sample data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const coursesData = await getCourses();
        setCourses(coursesData);
        setFilteredCourses(coursesData);

        const professorsData = await getProfessors();
        setProfessors(professorsData);
        setFilteredProfessors(professorsData);
      } catch (err) {
        console.error("Failed to load data:", err);
      }
    };
    fetchData();
  }, []);

  // Filter courses based on search & category
  useEffect(() => {
    let filtered = courses;
    if (selectedCategory !== "all") {
      filtered = filtered.filter((course) => course.category === selectedCategory);
    }
    if (searchQuery) {
      filtered = filtered.filter(
        (c) =>
          c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.instructor.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    setFilteredCourses(filtered);

    // Filter professors by search query
    let profFiltered = professors;
    if (searchQuery) {
      profFiltered = profFiltered.filter((p) =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.department.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    setFilteredProfessors(profFiltered);
  }, [searchQuery, selectedCategory, courses, professors]);

  return (
    <div className="landing-page">
      {/* Header */}
      <header className="landing-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="logo-title">📚 EduHub</h1>
          </div>
          <div className="profile-section">
            <div className="user-profile">
              <span className="username">{user?.username || "User"}</span>
              <button className="logout-btn" onClick={onLogout}>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

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

        {/* Categories */}
        <div className="categories-section">
          <h2>Categories</h2>
          <div className="categories-grid">
            {categories.map((category) => (
              <button
                key={category.id}
                className={`category-btn ${selectedCategory === category.id ? "active" : ""}`}
                onClick={() => setSelectedCategory(category.id)}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>

        {/* Courses */}
        <div className="courses-section">
          <h2>
            {selectedCategory === "all"
              ? "All Courses"
              : `${categories.find((c) => c.id === selectedCategory)?.name}`}
          </h2>
          <div className="courses-grid">
            {filteredCourses.length > 0 ? (
              filteredCourses.map((course) => (
                <div key={course.id} className="course-card">
                  <div className="course-image">{course.image}</div>
                  <div className="course-content">
                    <h3>{course.title}</h3>
                    <p className="instructor">👨‍🏫 {course.instructor}</p>
                    <div className="course-meta">
                      <span className="students">👥 {course.students} students</span>
                      <span className="rating">⭐ {course.rating}</span>
                    </div>
                    <Link to={`/courses/${course.id}`}>
                      <button className="enroll-btn">View Details</button>
                    </Link>
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
                  <h3>{prof.name}</h3>
                  <p>🏛 {prof.department}</p>
                  <Link to={`/professors/${prof.id}`}>
                    <button className="view-btn">View Reviews</button>
                  </Link>
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
