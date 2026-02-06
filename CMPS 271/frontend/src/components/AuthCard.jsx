import { useState, useEffect } from "react"

function AuthCard() {
  const [mode, setMode] = useState("signin")
  const [email, setEmail] = useState("")
  const [otp, setOtp] = useState("")
  const [otpStep, setOtpStep] = useState(false)
  const [error, setError] = useState("")

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

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!email.endsWith("@mail.aub.edu")) {
      setError("Only AUB email addresses are allowed")
      return
    }

    setError("")

    // Start Microsoft/AUB OAuth login via backend (Sprint 1)
    if (!otpStep) {
      window.location.href = "http://localhost:8000/auth/login"
      return
    }

    // (kept for now, but you won't reach this anymore unless you manually set otpStep=true)
    console.log("Verify OTP:", { email, otp })
  }

  const handleResend = () => {
    console.log("Resend OTP to:", email)
    setResendTimer(30)
    setCanResend(false)
  }

  return (
    <div className="auth-card">
      <h2>Welcome Back</h2>
      <p>Sign in to access course reviews and community discussions</p>

      <div className="tabs">
        <button
          className={mode === "signin" ? "active" : ""}
          onClick={() => {
            setMode("signin")
            setOtpStep(false)
            setOtp("")
          }}
          type="button"
        >
          Sign In
        </button>
        <button
          className={mode === "signup" ? "active" : ""}
          onClick={() => {
            setMode("signup")
            setOtpStep(false)
            setOtp("")
          }}
          type="button"
        >
          Sign Up
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <label>Email Address</label>
        <input
          type="email"
          placeholder="student@mail.aub.edu"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
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
              disabled={!canResend}
              onClick={handleResend}
            >
              {canResend ? "Send again" : `Send again in ${resendTimer}s`}
            </button>
          </>
        )}

        {error && <span className="error">{error}</span>}

        <button type="submit" className="submit-btn">
          {!otpStep
            ? mode === "signin"
              ? "Sign In"
              : "Create Account"
            : "Verify OTP"}
        </button>
      </form>

      <hr />

      <p className="terms">
        By continuing, you agree to our <a>Terms of Service</a> and{" "}
        <a>Privacy Policy</a>
      </p>

      <p className="support">
        Need help? <a>Contact Support</a>
      </p>
    </div>
  )
}

export default AuthCard