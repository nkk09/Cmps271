import { useState, useEffect } from "react"

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
        if (prev <= 1) {
          clearInterval(interval)
          setCanResend(true)
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [otpStep, canResend])

  const backend = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"

  const placeholderForRole = role === "student" ? "student@mail.aub.edu" : "prof@aub.edu.lb"

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (loading) return

    const lower = (email || "").toLowerCase().trim()
    if (role === "student") {
      if (!lower.endsWith("@mail.aub.edu")) {
        setError("Student email must end with @mail.aub.edu")
        return
      }
    } else {
      if (!lower.endsWith("@aub.edu.lb")) {
        setError("Professor email must end with @aub.edu.lb")
        return
      }
    }

    setError("")
    setLoading(true)
    console.log("[AuthCard] setLoading(true) - email:", lower)

    // Try OTP flow first. If backend responds that OTP is disabled (OAuth enabled), fallback to OAuth redirect.
    try {
      console.log("[AuthCard] Fetching:", `${backend}/auth/otp/send`)
      const resp = await fetch(`${backend}/auth/otp/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: lower }),
        credentials: "include",
      })

      if (resp.ok) {
        setOtpStep(true)
        setResendTimer(30)
        setCanResend(false)
        setLoading(false)
        return
      }

      const text = await resp.text().catch(() => "")
      console.debug("OTP send response", { url: `${backend}/auth/otp/send`, status: resp.status, body: text })
      let data = {}
      try {
        data = JSON.parse(text || "{}")
      } catch (e) {
        data = {}
      }
      // If OTP disabled, start OAuth login
      if (resp.status === 400 && typeof data.detail === "string" && data.detail.includes("OTP disabled")) {
        window.location.href = `${backend}/auth/login`
        return
      }

      setLoading(false)
      setError((data && data.detail) || `Failed to start login (${resp.status})`)
    } catch (err) {
      console.log("[AuthCard] Error caught:", err.message || err)
      setLoading(false)
      setError("Network error: " + (err && err.message ? err.message : String(err)))
    }
  }

  const handleVerify = async (e) => {
    e.preventDefault()
    if (loading) return
    setError("")
    setLoading(true)
    try {
      const resp = await fetch(`${backend}/auth/otp/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.toLowerCase().trim(), code: otp }),
        credentials: "include",
      })

      if (resp.ok) {
        // Logged in; call callback to update app state
        if (onLoginSuccess) {
          onLoginSuccess()
        } else {
          window.location.href = "/"
        }
        return
      }

      const text = await resp.text().catch(() => "")
      console.debug("OTP verify response", { url: `${backend}/auth/otp/verify`, status: resp.status, body: text })
      let data = {}
      try {
        data = JSON.parse(text || "{}")
      } catch (e) {
        data = {}
      }
      setLoading(false)
      setError((data && data.detail) || `Verification failed (${resp.status})`)
    } catch (err) {
      setLoading(false)
      setError("Network error contacting backend")
    }
  }

  const handleResend = async () => {
    if (loading) return
    setError("")
    setLoading(true)
    try {
      const resp = await fetch(`${backend}/auth/otp/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.toLowerCase().trim() }),
        credentials: "include",
      })
      if (resp.ok) {
        setResendTimer(30)
        setCanResend(false)
        setLoading(false)
        return
      }
      const text = await resp.text().catch(() => "")
      console.debug("OTP resend response", { url: `${backend}/auth/otp/send`, status: resp.status, body: text })
      let data = {}
      try {
        data = JSON.parse(text || "{}")
      } catch (e) {
        data = {}
      }
      setLoading(false)
      setError((data && data.detail) || `Failed to resend (${resp.status})`)
    } catch (err) {
      setLoading(false)
      setError("Network error contacting backend")
    }
  }

  return (
    <div className="auth-card">
      <h2>Welcome</h2>
      <p>Continue with your AUB email to access course reviews and discussions</p>

      <div className="role-tabs">
        <button
          type="button"
          className={role === "student" ? "active" : ""}
          onClick={() => {
            setRole("student")
            setEmail("")
            setError("")
            setOtpStep(false)
            setOtp("")
          }}
          disabled={loading}
        >
          Student
        </button>
        <button
          type="button"
          className={role === "professor" ? "active" : ""}
          onClick={() => {
            setRole("professor")
            setEmail("")
            setError("")
            setOtpStep(false)
            setOtp("")
          }}
          disabled={loading}
        >
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
              placeholder="Enter OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              required
            />

            <button
              type="button"
              className="resend-btn"
              disabled={!canResend || loading}
              onClick={handleResend}
            >
              {canResend ? "Send again" : `Send again in ${resendTimer}s`}
            </button>
          </>
        )}

        {error && <span className="error">{error}</span>}

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? "Loading..." : otpStep ? "Verify OTP" : "Continue with AUB email"}
        </button>
      </form>

      <hr />

      <p className="terms">
        By continuing, you agree to our <a>Terms of Service</a> and <a>Privacy Policy</a>
      </p>

      <p className="support">Need help? <a>Contact Support</a></p>
    </div>
  )
}

export default AuthCard