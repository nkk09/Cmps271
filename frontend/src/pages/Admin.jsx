import { useEffect, useMemo, useRef, useState } from "react"
import api from "../api"
import "../styles/admin.css"

const STATUS_OPTIONS = ["open", "in_review", "resolved", "dismissed"]
const SEVERITY_OPTIONS = ["low", "medium", "high", "critical"]
const TYPE_OPTIONS = ["spam", "harassment", "hate_speech", "misinformation", "personal_data", "other"]
const USER_STATUS_OPTIONS = ["active", "suspended", "inactive"]
const ROLE_OPTIONS = ["admin", "professor", "student"]

function Admin({ user }) {
  const [violations, setViolations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [severityFilter, setSeverityFilter] = useState("")
  const [typeFilter, setTypeFilter] = useState("")
  const [searchFilter, setSearchFilter] = useState("")
  const [savingId, setSavingId] = useState("")
  const [users, setUsers] = useState([])
  const [usersLoading, setUsersLoading] = useState(false)
  const [usersError, setUsersError] = useState("")
  const [usersSavingId, setUsersSavingId] = useState("")
  const [userRoleFilter, setUserRoleFilter] = useState("")
  const [userStatusFilter, setUserStatusFilter] = useState("")
  const [userSearch, setUserSearch] = useState("")
  const [pendingReviews, setPendingReviews] = useState([])
  const [pendingLoading, setPendingLoading] = useState(false)
  const [moderatingId, setModeratingId] = useState("")

  const isAdmin = user?.roles?.includes("admin")

  const violationsRef = useRef(null)
  const recentReviewsRef = useRef(null)
  const pendingReviewsRef = useRef(null)
  const usersRef = useRef(null)

  const scrollTo = (ref) => ref.current?.scrollIntoView({ behavior: "smooth", block: "start" })

  const loadViolations = async () => {
    if (!isAdmin) return
    setLoading(true)
    setError("")
    try {
      const params = {}
      if (statusFilter) params.status_filter = statusFilter
      if (severityFilter) params.severity = severityFilter
      if (typeFilter) params.violation_type = typeFilter
      if (searchFilter.trim().length >= 2) params.search = searchFilter.trim()
      const data = await api.violations.list(params)
      setViolations((data || []).map((v) => ({ ...v, draft_notes: v.admin_notes || "" })))
    } catch (err) {
      setError(err.message || "Failed to load moderation cases")
      setViolations([])
    } finally {
      setLoading(false)
    }
  }

  const loadPendingReviews = async () => {
    if (!isAdmin) return
    setPendingLoading(true)
    try {
      const data = await api.reviews.listPending()
      setPendingReviews(data || [])
    } catch {
      setPendingReviews([])
    } finally {
      setPendingLoading(false)
    }
  }

  useEffect(() => {
    loadViolations()
    loadPendingReviews()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, severityFilter, typeFilter, searchFilter, isAdmin])

  const loadUsers = async () => {
    if (!isAdmin) return
    setUsersLoading(true)
    setUsersError("")
    try {
      const params = {}
      if (userRoleFilter) params.role = userRoleFilter
      if (userStatusFilter) params.status_filter = userStatusFilter
      if (userSearch.trim().length >= 2) params.search = userSearch.trim()
      const data = await api.users.adminList(params)
      setUsers((data || []).map((u) => ({
        ...u,
        draft_roles: u.roles || [],
        draft_status: u.status,
      })))
    } catch (err) {
      setUsersError(err.message || "Failed to load users")
      setUsers([])
    } finally {
      setUsersLoading(false)
    }
  }

  useEffect(() => {
    const t = setTimeout(() => {
      loadUsers()
    }, 250)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin, userRoleFilter, userStatusFilter, userSearch])

  const stats = useMemo(() => {
    const openCount = violations.filter((v) => v.status === "open").length
    const inReviewCount = violations.filter((v) => v.status === "in_review").length
    const resolvedCount = violations.filter((v) => v.status === "resolved").length
    return { total: violations.length, open: openCount, inReview: inReviewCount, resolved: resolvedCount }
  }, [violations])

  const recentViolationCases = useMemo(() => {
    return violations
      .slice()
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5)
  }, [violations])

  const patchLocal = (id, patch) => {
    setViolations((prev) => prev.map((v) => (v.id === id ? { ...v, ...patch } : v)))
  }

  const patchUserLocal = (id, patch) => {
    setUsers((prev) => prev.map((u) => (u.id === id ? { ...u, ...patch } : u)))
  }

  const saveViolation = async (violation) => {
    setSavingId(violation.id)
    setError("")
    try {
      const payload = {
        status: violation.status,
        severity: violation.severity,
        admin_notes: violation.draft_notes,
      }
      const updated = await api.violations.update(violation.id, payload)
      patchLocal(violation.id, {
        ...updated,
        draft_notes: updated.admin_notes || "",
      })
    } catch (err) {
      setError(err.message || "Failed to save moderation update")
    } finally {
      setSavingId("")
    }
  }

  const toggleRole = (userId, roleName, checked) => {
    const target = users.find((u) => u.id === userId)
    if (!target) return
    const nextRoles = checked
      ? Array.from(new Set([...(target.draft_roles || []), roleName]))
      : (target.draft_roles || []).filter((r) => r !== roleName)
    patchUserLocal(userId, { draft_roles: nextRoles })
  }

  const saveUserRoles = async (u) => {
    if (!u.draft_roles || u.draft_roles.length === 0) {
      setUsersError("Each user must keep at least one role.")
      return
    }
    setUsersSavingId(`roles:${u.id}`)
    setUsersError("")
    try {
      const updated = await api.users.adminUpdateRoles(u.id, u.draft_roles)
      patchUserLocal(u.id, {
        ...updated,
        draft_roles: updated.roles,
        draft_status: updated.status,
      })
    } catch (err) {
      setUsersError(err.message || "Failed to update user roles")
    } finally {
      setUsersSavingId("")
    }
  }

  const saveUserStatus = async (u) => {
    setUsersSavingId(`status:${u.id}`)
    setUsersError("")
    try {
      const updated = await api.users.adminUpdateStatus(u.id, u.draft_status)
      patchUserLocal(u.id, {
        ...updated,
        draft_roles: updated.roles,
        draft_status: updated.status,
      })
    } catch (err) {
      setUsersError(err.message || "Failed to update user status")
    } finally {
      setUsersSavingId("")
    }
  }

  const moderateReview = async (reviewId, newStatus) => {
    setModeratingId(`${newStatus}:${reviewId}`)
    try {
      await api.reviews.updateStatus(reviewId, newStatus)
      setPendingReviews((prev) => prev.filter((r) => r.id !== reviewId))
    } catch (err) {
      setError(err.message || "Failed to moderate review")
    } finally {
      setModeratingId("")
    }
  }

  if (!isAdmin) {
    return (
      <div className="admin-page">
        <div className="admin-inner">
          <h1>Admin Moderation</h1>
          <p className="admin-empty">You do not have access to this page.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="admin-page">
      <div className="admin-inner">
        <header className="admin-header">
          <div>
            <h1>Admin Moderation Panel</h1>
            <p>Review and triage reported content violations.</p>
          </div>
          <button onClick={loadViolations} className="admin-refresh-btn" disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </header>
        <section className="admin-actions">
          <button className="admin-save-btn" type="button" onClick={() => scrollTo(pendingReviewsRef)}>Pending Reviews</button>
          <button className="admin-save-btn" type="button" onClick={() => scrollTo(usersRef)}>View Users</button>
          <button className="admin-save-btn" type="button" onClick={() => scrollTo(violationsRef)}>View Violations</button>
          <button className="admin-save-btn" type="button" onClick={() => scrollTo(recentReviewsRef)}>View Reports</button>
        </section>


        <section className="admin-stats">
          <article>
            <h3>{stats.total}</h3>
            <p>Total Cases</p>
          </article>
          <article>
            <h3>{stats.open}</h3>
            <p>Open</p>
          </article>
          <article>
            <h3>{stats.inReview}</h3>
            <p>In Review</p>
          </article>
          <article>
            <h3>{stats.resolved}</h3>
            <p>Resolved</p>
          </article>
        </section>

        <section className="admin-filters">
          <div className="admin-field">
            <label>Status</label>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All</option>
              {STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>

          <div className="admin-field">
            <label>Severity</label>
            <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
              <option value="">All</option>
              {SEVERITY_OPTIONS.map((severity) => (
                <option key={severity} value={severity}>{severity}</option>
              ))}
            </select>
          </div>

          <div className="admin-field">
            <label>Type</label>
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="">All</option>
              {TYPE_OPTIONS.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className="admin-field admin-search-field">
            <label>Search</label>
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Search review text, reporter, or review ID"
            />
          </div>
        </section>

        {error && <div className="admin-error">{error}</div>}

        {/* Pending Reviews Moderation */}
        <section className="admin-list" ref={pendingReviewsRef}>
          <header className="admin-subheader">
            <div>
              <h2>Pending Reviews ({pendingReviews.length})</h2>
              <p>Reviews awaiting approval before they are visible to other users.</p>
            </div>
            <button onClick={loadPendingReviews} className="admin-refresh-btn" disabled={pendingLoading}>
              {pendingLoading ? "Refreshing..." : "Refresh"}
            </button>
          </header>
          {!pendingLoading && pendingReviews.length === 0 && (
            <p className="admin-empty">No reviews pending approval.</p>
          )}
          {pendingReviews.map((r) => (
            <article key={r.id} className="admin-card">
              <div className="admin-card-row">
                <span className="chip">By: {r.student?.username || "unknown"}</span>
                <span className={`chip chip-severity chip-medium`}>Rating: {r.rating}/5</span>
                <span className="chip">Submitted: {new Date(r.created_at).toLocaleString()}</span>
              </div>
              <p><strong>Review ID:</strong> {r.id}</p>
              <p style={{ marginTop: "8px" }}>{r.content}</p>
              <div className="admin-card-controls" style={{ marginTop: "14px" }}>
                <button
                  className="admin-save-btn"
                  onClick={() => moderateReview(r.id, "approved")}
                  disabled={!!moderatingId}
                >
                  {moderatingId === `approved:${r.id}` ? "Approving..." : "Approve"}
                </button>
                <button
                  className="admin-refresh-btn"
                  onClick={() => moderateReview(r.id, "rejected")}
                  disabled={!!moderatingId}
                  style={{ marginLeft: "10px" }}
                >
                  {moderatingId === `rejected:${r.id}` ? "Rejecting..." : "Reject"}
                </button>
              </div>
            </article>
          ))}
        </section>

        {!loading && violations.length === 0 && (
          <p className="admin-empty">No moderation cases found for the selected filters.</p>
        )}

        {recentViolationCases.length > 0 && (
          <section className="admin-list" ref={recentReviewsRef}>
            <header className="admin-subheader">
              <div>
                <h2>Recent Reported Reviews</h2>
                <p>Newest review reports that need moderation attention.</p>
              </div>
            </header>
            {recentViolationCases.map((v) => (
              <article key={`recent-${v.id}`} className="admin-card">
                <div className="admin-card-row">
                  <span className="chip">Review ID: {v.review_id}</span>
                  <span className="chip">Type: {v.violation_type}</span>
                  <span className={`chip chip-severity chip-${v.severity}`}>Severity: {v.severity}</span>
                </div>
                <p><strong>Status:</strong> {v.status}</p>
                <p><strong>Reported:</strong> {new Date(v.created_at).toLocaleString()}</p>
                <p><strong>Reason:</strong> {v.reason || "No reason provided"}</p>
              </article>
            ))}
          </section>
        )}

        <section className="admin-list" ref={violationsRef}>
          {violations.map((v) => (
            <article key={v.id} className="admin-card">
              <div className="admin-card-row">
                <span className="chip">Type: {v.violation_type}</span>
                <span className={`chip chip-severity chip-${v.severity}`}>Severity: {v.severity}</span>
                <span className="chip">Status: {v.status}</span>
              </div>

              <p><strong>Case ID:</strong> {v.id}</p>
              <p><strong>Review ID:</strong> {v.review_id}</p>
              <p><strong>Reported Review Author:</strong> {v.review?.student?.username || "unknown"}</p>
              <p><strong>Reporter:</strong> {v.reported_by_student?.username || v.reported_by_student_id || "anonymous"}</p>
              <p><strong>Reason:</strong> {v.reason || "No reason provided"}</p>
              <p><strong>Created:</strong> {new Date(v.created_at).toLocaleString()}</p>
              <p><strong>Resolved:</strong> {v.resolved_at ? new Date(v.resolved_at).toLocaleString() : "-"}</p>
              <div style={{ marginTop: "12px" }}>
                <p><strong>Reported Review</strong></p>
                <p>{v.review?.content || "No review content available."}</p>
              </div>
              <div className="admin-card-controls">
                <div className="admin-field">
                  <label>Update Status</label>
                  <select value={v.status} onChange={(e) => patchLocal(v.id, { status: e.target.value })}>
                    {STATUS_OPTIONS.map((status) => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                </div>

                <div className="admin-field">
                  <label>Update Severity</label>
                  <select value={v.severity} onChange={(e) => patchLocal(v.id, { severity: e.target.value })}>
                    {SEVERITY_OPTIONS.map((severity) => (
                      <option key={severity} value={severity}>{severity}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="admin-field">
                <label>Admin Notes</label>
                <textarea
                  rows={4}
                  value={v.draft_notes}
                  onChange={(e) => patchLocal(v.id, { draft_notes: e.target.value })}
                  placeholder="Write moderation notes..."
                />
              </div>

              <button
                className="admin-save-btn"
                onClick={() => saveViolation(v)}
                disabled={savingId === v.id}
              >
                {savingId === v.id ? "Saving..." : "Save Changes"}
              </button>
            </article>
          ))}
        </section>

        <section className="admin-users" ref={usersRef}>
          <header className="admin-subheader">
            <div>
              <h2>User Management</h2>
              <p>Admins can manage account status and role assignments.</p>
            </div>
            <button onClick={loadUsers} className="admin-refresh-btn" disabled={usersLoading}>
              {usersLoading ? "Refreshing..." : "Refresh Users"}
            </button>
          </header>

          <div className="admin-user-filters">
            <div className="admin-field">
              <label>Role</label>
              <select value={userRoleFilter} onChange={(e) => setUserRoleFilter(e.target.value)}>
                <option value="">All</option>
                {ROLE_OPTIONS.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            <div className="admin-field">
              <label>Status</label>
              <select value={userStatusFilter} onChange={(e) => setUserStatusFilter(e.target.value)}>
                <option value="">All</option>
                {USER_STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div className="admin-field">
              <label>Search</label>
              <input
                type="text"
                value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)}
                placeholder="username or professor name"
              />
            </div>
          </div>

          {usersError && <div className="admin-error">{usersError}</div>}

          {!usersLoading && users.length === 0 && (
            <p className="admin-empty">No users found for the current filters.</p>
          )}

          <div className="admin-user-list">
            {users.map((u) => (
              <article key={u.id} className="admin-user-card">
                <div className="admin-user-header">
                  <div>
                    <h3>{u.student_username || u.professor_name || "User"}</h3>
                    <p>ID: {u.id}</p>
                    <p>Created: {new Date(u.created_at).toLocaleDateString()}</p>
                    <p>Last Login: {u.last_login ? new Date(u.last_login).toLocaleString() : "Never"}</p>
                  </div>
                </div>

                <div className="admin-user-controls">
                  <div className="admin-field">
                    <label>Status</label>
                    <select
                      value={u.draft_status}
                      onChange={(e) => patchUserLocal(u.id, { draft_status: e.target.value })}
                    >
                      {USER_STATUS_OPTIONS.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                    <button
                      className="admin-save-btn"
                      onClick={() => saveUserStatus(u)}
                      disabled={usersSavingId === `status:${u.id}`}
                    >
                      {usersSavingId === `status:${u.id}` ? "Saving..." : "Save Status"}
                    </button>
                  </div>

                  <div className="admin-field">
                    <label>Roles</label>
                    <div className="role-grid">
                      {ROLE_OPTIONS.map((roleName) => (
                        <label key={roleName} className="role-chip">
                          <input
                            type="checkbox"
                            checked={(u.draft_roles || []).includes(roleName)}
                            onChange={(e) => toggleRole(u.id, roleName, e.target.checked)}
                          />
                          <span>{roleName}</span>
                        </label>
                      ))}
                    </div>

                    <button
                      className="admin-save-btn"
                      onClick={() => saveUserRoles(u)}
                      disabled={usersSavingId === `roles:${u.id}`}
                    >
                      {usersSavingId === `roles:${u.id}` ? "Saving..." : "Save Roles"}
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

export default Admin
