import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const LINKS = [
  { to: "/", label: "Dashboard" },
  { to: "/organizations", label: "Organizations" },
  { to: "/projects", label: "Projects" },
  { to: "/queues", label: "Queues" },
  { to: "/jobs", label: "Jobs" },
  { to: "/workers", label: "Workers" },
  { to: "/dlq", label: "Dead Letter Queue" },
  { to: "/settings", label: "Settings" },
];

export function Sidebar({ open, onClose }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <aside className={`sidebar ${open ? "open" : ""}`} aria-label="Primary">
      <div className="sidebar-brand">Scheduler</div>
      <nav>
        {LINKS.map((link) => (
          <NavLink key={link.to} to={link.to} end={link.to === "/"} onClick={onClose}>
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div>{user?.email || user?.name || "Signed in"}</div>
        <button type="button" className="btn btn-ghost" onClick={handleLogout} style={{ marginTop: "0.5rem" }}>
          Log out
        </button>
      </div>
    </aside>
  );
}
