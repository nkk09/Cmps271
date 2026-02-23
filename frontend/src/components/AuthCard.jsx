import { useState, useEffect } from "react"
import api from "../api"

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

  const placeholderForRole = role === "student" ? "student@mail.aub.edu" : "prof@aub.edu.lb"

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (loading) return

    const lower = (email || "").toLowerCase().trim()
    if (role === "student" && !lower.endsWith("@mail.aub.edu")) {
      setError("Student email must end with @mail.aub.edu")
      return
    }
    if (role === "professor" && !lower.endsWith("@aub.edu.lb")) {
      setError("Professor email must end with @aub.edu.lb")
      return
    }

    setError("")
    setLoading(true)
    try {
      await api.auth.requestOtp(lower)
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
      // token is stored inside api.auth.verifyOtp
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
    setRole(newRole)
    setEmail("")
    setError("")
    setOtpStep(false)
    setOtp("")
  }

  return (
    <div className="auth-card">
      <h2>Welcome</h2>
      <p>Continue with your AUB email to access course reviews and discussions</p>

      <div className="role-tabs">
        <button
          type="button"
          className={role === "student" ? "active" : ""}
          onClick={() => switchRole("student")}
          disabled={loading}
        >
          Student
        </button>
        <button
          type="button"
          className={role === "professor" ? "active" : ""}
          onClick={() => switchRole("professor")}
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
              placeholder="Enter 6-digit code"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              required
              maxLength={6}
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