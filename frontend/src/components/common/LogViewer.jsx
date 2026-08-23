import { formatDate } from "../../utils/format";

export function LogViewer({ logs = [] }) {
  if (!logs.length) return <p className="muted">No execution logs recorded.</p>;
  return (
    <div className="log-viewer">
      {logs.map((log, index) => (
        <div className="log-row" key={log.id || `${log.timestamp}-${index}`}>
          <span className="log-time">{formatDate(log.timestamp || log.created_at)}</span>
          <span className={`log-level log-${String(log.level || "INFO").toLowerCase()}`}>{String(log.level || "INFO").toUpperCase()}</span>
          <span className="log-message">{log.message || "—"}</span>
        </div>
      ))}
    </div>
  );
}
