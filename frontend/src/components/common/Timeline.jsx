import { formatDate } from "../../utils/format";

const EVENT_LABELS = {
  created_at: "Created",
  scheduled_at: "Scheduled",
  claimed_at: "Claimed",
  started_at: "Running",
  completed_at: "Completed",
  failed_at: "Failed",
  cancelled_at: "Cancelled",
};

export function Timeline({ job, executions = [] }) {
  const events = Object.entries(EVENT_LABELS)
    .filter(([key]) => job?.[key])
    .map(([key, label]) => ({ key, label, at: job[key], worker: key === "claimed_at" ? job.worker_id : null }));

  if (job?.status === "RETRYING") events.push({ key: "retrying", label: "Retry scheduled", at: job.next_retry_at });
  if (job?.status === "DEAD_LETTER") events.push({ key: "dlq", label: "Moved to dead letter queue", at: job.failed_at || job.updated_at });

  const sorted = events.filter((item) => item.at).sort((a, b) => new Date(a.at) - new Date(b.at));

  return (
    <ol className="timeline">
      {sorted.length ? sorted.map((event) => (
        <li key={event.key} className="timeline-item">
          <span className="timeline-dot" />
          <div>
            <strong>{event.label}</strong>
            <div className="muted">{formatDate(event.at)}{event.worker ? ` · ${event.worker}` : ""}</div>
          </div>
        </li>
      )) : <li className="muted">No lifecycle events recorded yet.</li>}
      {executions.length > 1 ? <li className="timeline-note muted">{executions.length} execution attempts recorded.</li> : null}
    </ol>
  );
}
