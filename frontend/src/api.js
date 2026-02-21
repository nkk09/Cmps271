/**
 * API utilities for frontend
 * Handles all backend communication
 */

const API_BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"

const api = {
  // User endpoints
  async getCurrentUser() {
    const resp = await fetch(`${API_BASE}/api/users/me`, {
      credentials: "include",
    })
    if (!resp.ok) throw new Error("Failed to fetch current user")
    return resp.json()
  },

  // Course endpoints
  async getCourses(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${API_BASE}/api/courses?${queryString}` : `${API_BASE}/api/courses`
    const resp = await fetch(url, { credentials: "include" })
    if (!resp.ok) throw new Error("Failed to fetch courses")
    return resp.json()
  },

  async getCourse(courseId) {
    const resp = await fetch(`${API_BASE}/api/courses/${courseId}`, {
      credentials: "include",
    })
    if (!resp.ok) throw new Error("Failed to fetch course")
    return resp.json()
  },

  async getSections(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${API_BASE}/api/courses/sections?${queryString}` : `${API_BASE}/api/courses/sections`
    const resp = await fetch(url, { credentials: "include" })
    if (!resp.ok) throw new Error("Failed to fetch sections")
    return resp.json()
  },

  async getSection(sectionId) {
    const resp = await fetch(`${API_BASE}/api/courses/sections/${sectionId}`, {
      credentials: "include",
    })
    if (!resp.ok) throw new Error("Failed to fetch section")
    return resp.json()
  },

  async getProfessors(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${API_BASE}/api/courses/professors?${queryString}` : `${API_BASE}/api/courses/professors`
    const resp = await fetch(url, { credentials: "include" })
    if (!resp.ok) throw new Error("Failed to fetch professors")
    return resp.json()
  },

  async getProfessor(professorId) {
    const resp = await fetch(`${API_BASE}/api/courses/professors/${professorId}`, {
      credentials: "include",
    })
    if (!resp.ok) throw new Error("Failed to fetch professor")
    return resp.json()
  },

  // Review endpoints
  async getReviews(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${API_BASE}/api/reviews?${queryString}` : `${API_BASE}/api/reviews`
    const resp = await fetch(url, { credentials: "include" })
    if (!resp.ok) throw new Error("Failed to fetch reviews")
    return resp.json()
  },

  async getReview(reviewId) {
    const resp = await fetch(`${API_BASE}/api/reviews/${reviewId}`, {
      credentials: "include",
    })
    if (!resp.ok) throw new Error("Failed to fetch review")
    return resp.json()
  },

  async createReview(reviewData) {
    const resp = await fetch(`${API_BASE}/api/reviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reviewData),
      credentials: "include",
    })
    if (!resp.ok) {
      const error = await resp.json().catch(() => ({}))
      throw new Error(error.detail || "Failed to create review")
    }
    return resp.json()
  },

  async updateReview(reviewId, updateData) {
    const resp = await fetch(`${API_BASE}/api/reviews/${reviewId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updateData),
      credentials: "include",
    })
    if (!resp.ok) {
      const error = await resp.json().catch(() => ({}))
      throw new Error(error.detail || "Failed to update review")
    }
    return resp.json()
  },

  async deleteReview(reviewId) {
    const resp = await fetch(`${API_BASE}/api/reviews/${reviewId}`, {
      method: "DELETE",
      credentials: "include",
    })
    if (!resp.ok) throw new Error("Failed to delete review")
  },

  async likeReview(reviewId) {
    const resp = await fetch(`${API_BASE}/api/reviews/${reviewId}/like`, {
      method: "POST",
      credentials: "include",
    })
    if (!resp.ok) throw new Error("Failed to like review")
    return resp.json()
  },

  async dislikeReview(reviewId) {
    const resp = await fetch(`${API_BASE}/api/reviews/${reviewId}/dislike`, {
      method: "POST",
      credentials: "include",
    })
    if (!resp.ok) throw new Error("Failed to dislike review")
    return resp.json()
  },
}

export default api
