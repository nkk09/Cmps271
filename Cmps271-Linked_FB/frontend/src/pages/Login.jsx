import LeftPanel from "../components/LeftPanel";
import AuthCard from "../components/AuthCard";
import "../styles/login.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function Login() {
  const handleLogin = () => {
    // Backend uses OAuth/session login -> redirect to backend login endpoint
    window.location.assign(`${API_BASE_URL}/auth/login`);
  };

  return (
    <div className="login-page">
      <LeftPanel />
      {/* AuthCard should contain the login button. We pass the handler to it. */}
      <AuthCard onLogin={handleLogin} />
    </div>
  );
}

export default Login;