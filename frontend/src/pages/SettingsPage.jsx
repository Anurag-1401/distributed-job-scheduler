import { PageHeader } from "../components/PageHeader";
import { useSettings } from "../context/SettingsContext";
import { useAuth } from "../context/AuthContext";
import { useState } from "react";

export function SettingsPage() {
  const { pollIntervalMs, setPollInterval, apiBaseUrl } = useSettings();
  const { user } = useAuth();
  const [saved, setSaved] = useState(false);
  const seconds = Math.round(pollIntervalMs / 1000);

  function save(event) {
    event.preventDefault();
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1800);
  }

  return (
    <div>
      <PageHeader title="Settings" subtitle="Operational preferences for the dashboard." />
      <div className="settings-grid">
        <form className="card" onSubmit={save}>
          <h2>Dashboard</h2>
          <div className="field"><label htmlFor="polling">Polling interval</label>
            <select id="polling" value={seconds} onChange={(e) => setPollInterval(Number(e.target.value) * 1000)}>
              <option value="3">3 seconds</option><option value="5">5 seconds</option><option value="10">10 seconds</option><option value="30">30 seconds</option>
            </select>
          </div>
          <button className="btn" type="submit">{saved ? "Saved" : "Save preferences"}</button>
        </form>
        <section className="card">
          <h2>Connection</h2>
          <dl className="detail-list"><div><dt>API endpoint</dt><dd className="mono">{apiBaseUrl}</dd></div><div><dt>Signed-in user</dt><dd>{user?.email || user?.name || "—"}</dd></div></dl>
          <p className="muted">The API URL is controlled by <span className="mono">VITE_API_BASE_URL</span>.</p>
        </section>
      </div>
    </div>
  );
}
