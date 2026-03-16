import LeftPanel from "../components/LeftPanel"
import AuthCard from "../components/AuthCard"
import "../styles/login.css"

function Login({ onLoginSuccess }) {
  return (
    <div className="login-page">
      <LeftPanel />
      <AuthCard onLoginSuccess={onLoginSuccess} />
    </div>
  )
}

export default Login
