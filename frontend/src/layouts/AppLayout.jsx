import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "../components/Sidebar";

export function AppLayout() {
  const [open, setOpen] = useState(false);

  return (
    <div className="app-shell">
      <div className={`overlay ${open ? "open" : ""}`} onClick={() => setOpen(false)} aria-hidden="true" />
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="content">
        <div className="topbar">
          <button type="button" className="menu-btn" onClick={() => setOpen(true)} aria-label="Open navigation">
            Menu
          </button>
          <strong>Scheduler</strong>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
