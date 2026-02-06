const API = import.meta.env.VITE_API_BASE_URL;

export function startLogin() {
  // Redirect browser to backend OAuth login
  window.location.assign(`${API}/login`);
}

export async function getMe() {
  const res = await fetch(`${API}/me`, { credentials: "include" });
  if (!res.ok) throw new Error("Not logged in");
  return res.json();
}

export async function logout() {
  const res = await fetch(`${API}/logout`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) throw new Error("Logout failed");
  return res.json();
}