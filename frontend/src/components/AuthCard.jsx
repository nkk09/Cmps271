import { useState, useEffect } from "react"
import api from "../api"

// Set VITE_ENABLE_OAUTH=true in frontend/.env to show the Microsoft button
// and hide the OTP form. Must match ENABLE_OAUTH on the backend.
const USE_OAUTH = import.meta.env.VITE_ENABLE_OAUTH === "true"

function AuthCard({ onLoginSuccess }) {
  const [role, setRole] = useState("student")
  const [email, setEmail] = useState("")
  const [otp, setOtp] = useState("")
  const [otpStep, setOtpStep] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [resendTimer, setResendTimer] = useState(30)
  const [canResend, setCanResend] = useState(false)

  useEffect(() => {
    if (!otpStep || canResend) return
    const interval = setInterval(() => {
      setResendTimer((prev) => {
        if (prev <= 1) { clearInterval(interval); setCanResend(true); return 0 }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [otpStep, canResend])

  // ── Entra OAuth handler ──────────────────────────────────────────────────
  const handleMicrosoftLogin = () => {
    api.auth.loginWithEntra()
    // Page will redirect — no state update needed
  }

  // ── OTP handlers ────────────────────────────────────────────────────────
  const placeholderForRole = role === "student" ? "student@mail.aub.edu" : "prof@aub.edu.lb"

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (loading) return
    const lower = (email || "").toLowerCase().trim()
    if (role === "student" && !lower.endsWith("@mail.aub.edu")) {
      setError("Student email must end with @mail.aub.edu"); return
    }
    if (role === "professor" && !lower.endsWith("@aub.edu.lb")) {
      setError("Professor email must end with @aub.edu.lb"); return
    }
    setError("")
    setLoading(true)
    try {
      const resp = await api.auth.requestOtp(lower)
      // If backend short-circuits to OAuth, it returns { oauth: true, auth_url }
      if (resp && resp.oauth && resp.auth_url) {
        // Redirect the browser to Microsoft's login page (full-page redirect required)
        window.location.href = resp.auth_url
        return
      }
      setOtpStep(true)
      setResendTimer(30)
      setCanResend(false)
    } catch (err) {
      setError(err.message || "Failed to send OTP")
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async (e) => {
    e.preventDefault()
    if (loading) return
    setError("")
    setLoading(true)
    try {
      await api.auth.verifyOtp(email.toLowerCase().trim(), otp)
      if (onLoginSuccess) onLoginSuccess()
    } catch (err) {
      setError(err.message || "Verification failed")
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (loading) return
    setError("")
    setLoading(true)
    try {
      await api.auth.requestOtp(email.toLowerCase().trim())
      setResendTimer(30)
      setCanResend(false)
    } catch (err) {
      setError(err.message || "Failed to resend OTP")
    } finally {
      setLoading(false)
    }
  }

  const switchRole = (newRole) => {
    setRole(newRole); setEmail(""); setError(""); setOtpStep(false); setOtp("")
  }

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <div className="auth-card">
      <h2>Welcome</h2>
      <p>Sign in with your AUB account to access course reviews</p>

      {USE_OAUTH ? (
        /* ── Microsoft Entra login ── */
        <div style={{ marginTop: "2rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <button
            type="button"
            className="submit-btn"
            onClick={handleMicrosoftLogin}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "10px",
              background: "#2f2f2f",
              fontSize: "15px",
            }}
          >
            <MicrosoftIcon />
            Sign in with Microsoft
          </button>
          <p style={{ textAlign: "center", fontSize: "13px", color: "#999", margin: 0 }}>
            Use your AUB Microsoft account (@mail.aub.edu or @aub.edu.lb)
          </p>
          {error && <span className="error">{error}</span>}
        </div>
      ) : (
        /* ── OTP fallback ── */
        <>
          <div className="role-tabs">
            <button type="button" className={role === "student" ? "active" : ""} onClick={() => switchRole("student")} disabled={loading}>
              Student
            </button>
            <button type="button" className={role === "professor" ? "active" : ""} onClick={() => switchRole("professor")} disabled={loading}>
              Professor
            </button>
          </div>

          <form onSubmit={otpStep ? handleVerify : handleSubmit}>
            <label>Email Address</label>
            <input
              type="email"
              placeholder={placeholderForRole}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={otpStep}
            />

            {otpStep && (
              <>
                <label>OTP Code</label>
                <input
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  required
                  maxLength={6}
                />
                <button type="button" className="resend-btn" disabled={!canResend || loading} onClick={handleResend}>
                  {canResend ? "Send again" : `Send again in ${resendTimer}s`}
                </button>
              </>
            )}

            {error && <span className="error">{error}</span>}

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? "Loading..." : otpStep ? "Verify OTP" : "Continue with AUB email"}
            </button>
          </form>
        </>
      )}

      <hr />
      <p className="terms">By continuing, you agree to our <a>Terms of Service</a> and <a>Privacy Policy</a></p>
      <p className="support">Need help? <a>Contact Support</a></p>
    </div>
  )
}

// Microsoft "waffle" logo as an inline SVG — no external dependency needed
function MicrosoftIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="1" width="9" height="9" fill="#f25022"/>
      <rect x="11" y="1" width="9" height="9" fill="#7fba00"/>
      <rect x="1" y="11" width="9" height="9" fill="#00a4ef"/>
      <rect x="11" y="11" width="9" height="9" fill="#ffb900"/>
    </svg>
  )
}

export default AuthCard