import React, { useEffect, useState } from "react";
import { getCourses } from "../services/api";

const CourseList = () => {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await getCourses();
        setCourses(response.data); // adjust if backend structure differs (check later)
      } catch (error) {
        console.error("Error fetching courses:", error);

        // TEMPORARY MOCK DATA, change later
        setCourses([
          { id: 1, name: "Database Systems", code: "CMPS 271", credits: 3 },
          { id: 2, name: "Operating Systems", code: "CMPS 352", credits: 4 }
        ]);
      }
    };

    fetchCourses();
  }, []);

  return (
    <div>
      <h2>Courses</h2>
      {courses.map((course) => (
        <div key={course.id} style={cardStyle}>
          <h3>{course.name}</h3>
          <p>Code: {course.code}</p>
          <p>Credits: {course.credits}</p>
        </div>
      ))}
    </div>
  );
};

const cardStyle = {
  border: "1px solid #ddd",
  padding: "10px",
  marginBottom: "10px",
  borderRadius: "8px",
};

export default CourseList;
