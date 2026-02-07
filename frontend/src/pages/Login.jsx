import LeftPanel from "../components/LeftPanel"
import AuthCard from "../components/AuthCard"
import "../styles/login.css"

function Login() {
  return (
    <div className="login-page">
      <LeftPanel />
      <AuthCard />
    </div>
  )
}

export default Login
