// src/api.js
import axios from "axios";

// CHANGE when backend is deployed
const API_BASE_URL = "http://localhost:8000";

// Axios instance for all API calls
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // cookies/session auth
});

// ------------------- Courses -------------------

// Get all courses
export const getCourses = async () => {
  // Returns array of courses: [{id, name, professor}, ...]
  const resp = await api.get("/courses");
  return resp.data;
};

// Get a single course by ID
export const getCourse = async (id) => {
  const resp = await api.get(`/courses/${id}`);
  return resp.data;
};

// ------------------- Reviews -------------------

// Get all reviews for a course
export const getReviews = async (courseId) => {
  const resp = await api.get(`/courses/${courseId}/reviews`);
  return resp.data;
};

// Create a new review for a course
export const createReview = async (courseId, review) => {
  // review = { comment: string, rating: number }
  const resp = await api.post(`/courses/${courseId}/reviews`, review);
  return resp.data;
};

// ------------------- Professors -------------------

// Get all professors
export const getProfessors = async () => {
  // Returns array of professors: [{id, name, department}, ...]
  const resp = await api.get("/professors");
  return resp.data;
};

// Get a single professor by ID
export const getProfessor = async (id) => {
  const resp = await api.get(`/professors/${id}`);
  return resp.data;
};

// Get all reviews for a professor
export const getProfessorReviews = async (professorId) => {
  const resp = await api.get(`/professors/${professorId}/reviews`);
  return resp.data;
};

// Create a new review for a professor
export const createProfessorReview = async (professorId, review) => {
  // review = { comment: string, rating: number }
  const resp = await api.post(`/professors/${professorId}/reviews`, review);
  return resp.data;
};

// ------------------- Auth -------------------

// Get currently logged-in user
export const getCurrentUser = async () => {
  const resp = await api.get("/auth/me");
  return resp.data;
};

// Logout user
export const logout = async () => {
  await api.post("/auth/logout");
};

export default api;