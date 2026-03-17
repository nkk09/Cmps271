/**
 * API client for AfterClass backend.
 * Uses JWT Bearer tokens stored in localStorage.
 */

const BASE = (import.meta.env.VITE_BACKEND_URL || "http://localhost:8000") + "/api/v1"

// ---------------------------------------------------------------------------
// Token management
// ---------------------------------------------------------------------------

export const token = {
  get: () => localStorage.getItem("access_token"),
  set: (t) => localStorage.setItem("access_token", t),
  clear: () => localStorage.removeItem("access_token"),
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers }
  const t = token.get()
  if (t) headers["Authorization"] = `Bearer ${t}`

  const resp = await fetch(`${BASE}${path}`, { ...options, headers })

  if (resp.status === 401) {
    token.clear()
    window.dispatchEvent(new Event("auth:expired"))
    throw new Error("Session expired. Please log in again.")
  }

  if (resp.status === 204) return null

  const data = await resp.json().catch(() => ({}))

  if (!resp.ok) {
    throw new Error(data.detail || `Request failed (${resp.status})`)
  }

  return data
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

const auth = {
  async requestOtp(email) {
    return request("/auth/request-otp", {
      method: "POST",
      body: JSON.stringify({ email }),
    })
  },

  async verifyOtp(email, code) {
    const data = await request("/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ email, code }),
    })
    token.set(data.access_token)
    return data
  },

  async logout() {
    await request("/auth/logout", { method: "POST" }).catch(() => {})
    token.clear()
  },

  isLoggedIn() {
    return !!token.get()
  },

  /**
   * Redirect to the backend Entra login endpoint.
   * After auth, the backend redirects to FRONTEND_URL/auth/callback?token=<jwt>
   */
  loginWithEntra() {
    const base = (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000') + '/api/v1'
    window.location.href = `${base}/auth/login`
  },
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

const users = {
  async getMe() {
    return request("/users/me")
  },

  async updateMe(data) {
    return request("/users/me", {
      method: "PATCH",
      body: JSON.stringify(data),
    })
  },

  async deleteMe() {
    return request("/users/me", { method: "DELETE" })
  },

  async getMyReviews(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/users/me/reviews${q ? "?" + q : ""}`)
  },

  async adminList(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/users/admin/list${q ? "?" + q : ""}`)
  },

  async adminUpdateRoles(userId, roles) {
    return request(`/users/admin/${userId}/roles`, {
      method: "PATCH",
      body: JSON.stringify({ roles }),
    })
  },

  async adminUpdateStatus(userId, statusValue) {
    return request(`/users/admin/${userId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: statusValue }),
    })
  },
}

// ---------------------------------------------------------------------------
// Courses
// ---------------------------------------------------------------------------

const courses = {
  async list(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/courses${q ? "?" + q : ""}`)
  },

  async get(courseId) {
    return request(`/courses/${courseId}`)
  },

  async getSections(courseId, params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/courses/${courseId}/sections${q ? "?" + q : ""}`)
  },

  async getDepartments() {
    return request("/courses/departments")
  },
}

// ---------------------------------------------------------------------------
// Professors
// ---------------------------------------------------------------------------

const professors = {
  async list(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/professors${q ? "?" + q : ""}`)
  },

  async get(professorId) {
    return request(`/professors/${professorId}`)
  },

  async getSections(professorId, params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/professors/${professorId}/sections${q ? "?" + q : ""}`)
  },

  async getReviews(professorId, params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/professors/${professorId}/reviews${q ? "?" + q : ""}`)
  },
}

// ---------------------------------------------------------------------------
// Sections
// ---------------------------------------------------------------------------

const sections = {
  async get(sectionId) {
    return request(`/sections/${sectionId}`)
  },

  async getReviews(sectionId, params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/sections/${sectionId}/reviews${q ? "?" + q : ""}`)
  },

  async createReview(sectionId, data) {
    return request(`/sections/${sectionId}/reviews`, {
      method: "POST",
      body: JSON.stringify(data),
    })
  },
}

// ---------------------------------------------------------------------------
// Semesters
// ---------------------------------------------------------------------------

const semesters = {
  async list() {
    return request("/semesters")
  },

  async getCurrent() {
    return request("/semesters/current")
  },
}

// ---------------------------------------------------------------------------
// Reviews
// ---------------------------------------------------------------------------

const reviews = {
  async listPending(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/reviews/pending${q ? "?" + q : ""}`)
  },

  async updateStatus(reviewId, status) {
    return request(`/reviews/${reviewId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    })
  },

  async update(reviewId, data) {
    return request(`/reviews/${reviewId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    })
  },

  async delete(reviewId) {
    return request(`/reviews/${reviewId}`, { method: "DELETE" })
  },

  async like(reviewId) {
    return request(`/reviews/${reviewId}/like`, { method: "POST" })
  },

  async dislike(reviewId) {
    return request(`/reviews/${reviewId}/dislike`, { method: "POST" })
  },

  async removeInteraction(reviewId) {
    return request(`/reviews/${reviewId}/interaction`, { method: "DELETE" })
  },
}

// ---------------------------------------------------------------------------
// Violations
// ---------------------------------------------------------------------------

const violations = {
  async report(reviewId, data) {
    return request(`/reviews/${reviewId}/violations`, {
      method: "POST",
      body: JSON.stringify(data),
    })
  },

  async list(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/violations${q ? "?" + q : ""}`)
  },

  async get(violationId) {
    return request(`/violations/${violationId}`)
  },

  async update(violationId, data) {
    return request(`/violations/${violationId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    })
  },
}

// ---------------------------------------------------------------------------
// Export
// ---------------------------------------------------------------------------

const api = { auth, users, courses, professors, sections, semesters, reviews, violations, token }
export default api