import { useCallback, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { StatCard } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import { getWorker, listWorkerJobs } from "../services/workerService";
import { getErrorMessage } from "../utils/errors";
import { formatDate, shortId } from "../utils/format";
import { usePolling } from "../hooks/usePolling";
import { useSettings } from "../context/SettingsContext";

export function WorkerDetailPage() {
  const { id } = useParams(); const { pollIntervalMs } = useSettings(); const [worker, setWorker] = useState(null); const [jobs, setJobs] = useState([]); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const load = useCallback(async () => { try { const data = await getWorker(id); setWorker(data); const current = await listWorkerJobs(id, { limit: 20 }).catch(() => ({ items: data.current_jobs || [] })); setJobs(Array.isArray(current) ? current : current.items || current.results || []); setError(""); } catch (err) { setError(getErrorMessage(err)); } finally { setLoading(false); } }, [id]);
  usePolling(load, pollIntervalMs, true);
  if (loading) return <LoadingState />; if (error && !worker) return <ErrorState onRetry={load}>{error}</ErrorState>; if (!worker) return <EmptyState title="Worker not found">The process may have been removed from the registry.</EmptyState>;
  const capacity = Number(worker.concurrency || worker.capacity || 0); const running = Number(worker.current_job_count ?? worker.running_jobs ?? 0); const utilization = worker.utilization ?? (capacity ? Math.round((running / capacity) * 100) : 0);
  return <div><PageHeader title="Worker detail" subtitle={<span className="mono">{worker.id || worker.worker_id}</span>} /><div className="worker-summary"><StatusBadge status={worker.status} /><span className="muted">Last heartbeat {formatDate(worker.last_heartbeat_at || worker.last_heartbeat)}</span></div><section className="stat-grid"><StatCard label="Concurrency" value={capacity || "—"} /><StatCard label="Active jobs" value={running} /><StatCard label="Utilization" value={`${utilization}%`} /><StatCard label="Completed" value={worker.completed_jobs} /><StatCard label="Failed" value={worker.failed_jobs} /><StatCard label="Uptime" value={worker.uptime || "—"} /></section><section className="detail-grid"><div className="card"><h2>Capacity</h2><div className="big-util"><strong>{utilization}%</strong><div className="util-track"><span style={{ width: `${Math.min(100, utilization)}%` }} /></div><p className="muted">{running} active of {capacity || "unknown"} slots</p></div></div><div className="card"><h2>Metadata</h2><pre className="mono code-block">{JSON.stringify(worker.metadata || {}, null, 2)}</pre></div></section><section className="card section-gap"><h2>Current jobs</h2>{jobs.length ? <div className="table-wrap"><table><thead><tr><th>Job</th><th>Queue</th><th>Status</th><th>Started</th></tr></thead><tbody>{jobs.map((job) => <tr key={job.id}><td><Link className="mono" to={`/jobs/${job.id}`}>{shortId(job.id)}</Link></td><td>{job.queue_name || shortId(job.queue_id)}</td><td><StatusBadge status={job.status} /></td><td>{formatDate(job.started_at)}</td></tr>)}</tbody></table></div> : <p className="muted">No current jobs.</p>}</section></div>;
}
