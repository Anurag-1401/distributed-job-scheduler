import { useCallback, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { StatusBadge } from "../components/StatusBadge";
import { Timeline } from "../components/common/Timeline";
import { LogViewer } from "../components/common/LogViewer";
import { cancelJob, getJob, listJobExecutions, listJobLogs, retryJob } from "../services/jobService";
import { retryDeadLetterJob } from "../services/dlqService";
import { getErrorMessage } from "../utils/errors";
import { unwrapList, formatDate, formatDuration } from "../utils/format";
import { usePolling } from "../hooks/usePolling";
import { useSettings } from "../context/SettingsContext";
import { useToast } from "../context/ToastContext";

export function JobDetailPage() {
  const { id } = useParams();
  const { pollIntervalMs } = useSettings();
  const { push } = useToast();
  const [job, setJob] = useState(null), [executions, setExecutions] = useState([]), [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true), [error, setError] = useState(""), [actionError, setActionError] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await getJob(id);
      setJob(data);
      const [ex, lg] = await Promise.all([listJobExecutions(id, { limit: 50 }).catch(() => ({ items: data.executions || [] })), listJobLogs(id, { limit: 100 }).catch(() => ({ items: data.logs || [] }))]);
      setExecutions(unwrapList(ex).items.length ? unwrapList(ex).items : data.executions || []);
      setLogs(unwrapList(lg).items.length ? unwrapList(lg).items : data.logs || []);
      setError("");
    } catch (err) { setError(getErrorMessage(err)); }
    finally { setLoading(false); }
  }, [id]);
  usePolling(load, pollIntervalMs, true);

  async function run(action, successMessage) {
    setActionError("");
    try { await action(); push(successMessage); await load(); }
    catch (err) { setActionError(getErrorMessage(err)); }
  }

  if (loading) return <LoadingState />;
  if (error && !job) return <ErrorState onRetry={load}>{error}</ErrorState>;
  if (!job) return <EmptyState title="Job not found">It may have been deleted or is outside your organization.</EmptyState>;

  const status = String(job.status || "").toUpperCase();
  const payload = typeof job.payload === "string" ? job.payload : JSON.stringify(job.payload ?? {}, null, 2);
  const policy = job.retry_policy || {};
  const canCancel = ["QUEUED", "SCHEDULED", "RETRYING", "CLAIMED"].includes(status);

  return <div>
    <PageHeader title="Job detail" subtitle={<span className="mono">{id}</span>} actions={<>
      {status !== "COMPLETED" && status !== "RUNNING" ? <button className="btn" onClick={() => run(() => retryJob(id), "Job retry scheduled")}>Retry</button> : null}
      {status === "DEAD_LETTER" ? <button className="btn btn-secondary" onClick={() => run(() => retryDeadLetterJob(job.dead_letter_id || id), "Job moved back to the queue")}>Retry from DLQ</button> : null}
      {canCancel ? <button className="btn btn-danger" onClick={() => run(() => cancelJob(id), "Job cancelled")}>Cancel</button> : null}
    </>} />
    {actionError ? <ErrorState title="Action failed">{actionError}</ErrorState> : null}
    {error ? <ErrorState title="Refresh failed">{error}</ErrorState> : null}

    <section className="detail-grid">
      <div className="card">
        <div className="detail-header"><div><StatusBadge status={job.status} /><h2>{job.type || job.job_type}</h2></div><Link to={`/queues/${job.queue_id}`}>{job.queue_name || job.queue_id}</Link></div>
        <dl className="detail-list">
          <div><dt>Priority</dt><dd>{job.priority ?? "—"}</dd></div><div><dt>Attempts</dt><dd>{job.attempts ?? job.attempt_count ?? 0}</dd></div><div><dt>Worker</dt><dd className="mono">{job.worker_id || "—"}</dd></div>
          <div><dt>Created</dt><dd>{formatDate(job.created_at)}</dd></div><div><dt>Scheduled</dt><dd>{formatDate(job.scheduled_at)}</dd></div><div><dt>Claimed</dt><dd>{formatDate(job.claimed_at)}</dd></div>
          <div><dt>Retry policy</dt><dd>{policy.strategy || "—"} · max {policy.max_attempts ?? "—"}</dd></div><div><dt>Next retry</dt><dd>{formatDate(job.next_retry_at)}</dd></div>
        </dl>
      </div>
      <div className="card"><h2>Lifecycle</h2><Timeline job={job} executions={executions} /></div>
    </section>

    <section className="card section-gap"><h2>Payload</h2><pre className="mono code-block">{payload}</pre></section>
    <section className="card section-gap"><h2>Execution history</h2>{executions.length ? <div className="table-wrap"><table><thead><tr><th>Attempt</th><th>Worker</th><th>Status</th><th>Start</th><th>End</th><th>Duration</th><th>Error</th></tr></thead><tbody>{executions.map((ex) => <tr key={ex.id || ex.attempt_number}><td>{ex.attempt_number}</td><td className="mono">{ex.worker_id || "—"}</td><td><StatusBadge status={ex.status} /></td><td>{formatDate(ex.started_at)}</td><td>{formatDate(ex.completed_at)}</td><td>{formatDuration(ex.duration_ms)}</td><td className="error-cell">{ex.error || "—"}</td></tr>)}</tbody></table></div> : <p className="muted">No execution attempts recorded.</p>}</section>
    <section className="card"><h2>Execution logs</h2><LogViewer logs={logs} /></section>
  </div>;
}
