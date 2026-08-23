export function HealthIndicator({ label, status, detail }) {
  const healthy = String(status || "").toLowerCase() === "healthy" || String(status || "").toLowerCase() === "online";
  return (
    <div className="health-row">
      <span className={`health-dot ${healthy ? "health-good" : "health-bad"}`} />
      <div>
        <strong>{label}</strong>
        <div className="muted">{detail || status || "Unknown"}</div>
      </div>
    </div>
  );
}
