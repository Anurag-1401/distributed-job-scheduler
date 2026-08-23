import { useCallback, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, BarChart, Bar } from "recharts";
import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { StatCard } from "../components/StatCard";
import { ErrorState, LoadingState } from "../components/Feedback";
import { HealthIndicator } from "../components/common/HealthIndicator";
import { StatusBadge } from "../components/StatusBadge";
import { usePolling } from "../hooks/usePolling";
import { useSettings } from "../context/SettingsContext";
import { getStats, getReady } from "../services/statsService";
import { listJobs } from "../services/jobService";
import { getErrorMessage } from "../utils/errors";
import { unwrapList, formatDate, shortId } from "../utils/format";

export function DashboardPage() {
  const { pollIntervalMs } = useSettings();
  const [stats, setStats] = useState(null);
  const [ready, setReady] = useState(null);
  const [recentJobs, setRecentJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const [overview, health, jobs] = await Promise.all([getStats(), getReady().catch(() => null), listJobs({ page: 1, limit: 8, sort: "created_at", order: "desc" }).catch(() => ({ items: [] }))]);
      setStats(overview);
      setReady(health);
      setRecentJobs(unwrapList(jobs).items);
      setError("");
    } catch (err) { setError(getErrorMessage(err)); }
    finally { setLoading(false); }
  }, []);

  usePolling(load, pollIntervalMs, true);

  if (loading) return <LoadingState message="Loading system health…" />;
  if (error && !stats) return <ErrorState onRetry={load}>{error}</ErrorState>;
  if (!stats) return <ErrorState>No metrics payload was returned.</ErrorState>;

  const jobsOverTime = stats.jobs_over_time || stats.throughput_series || [];
  const queueDepth = stats.queue_depth || [];
  const workerUtil = stats.worker_utilization || [];
  const successFailure = stats.success_failure || [{ name: "Completed", value: stats.completed_jobs || 0 }, { name: "Failed", value: stats.failed_jobs || 0 }];

  return <div>
    <PageHeader title="Dashboard" subtitle="Operational view of queues, workers, throughput, and failures." actions={<Link className="btn" to="/jobs/new">Create job</Link>} />
    {error ? <ErrorState title="Live refresh failed">{error}</ErrorState> : null}
    <section className="stat-grid">
      <StatCard label="Queues" value={stats.total_queues} />
      <StatCard label="Queued jobs" value={stats.queued_jobs} />
      <StatCard label="Running jobs" value={stats.running_jobs} />
      <StatCard label="Completed" value={stats.completed_jobs} />
      <StatCard label="Failed" value={stats.failed_jobs} />
      <StatCard label="DLQ" value={stats.dlq_jobs} />
      <StatCard label="Active workers" value={stats.active_workers} />
      <StatCard label="Throughput" value={stats.throughput} />
    </section>

    <section className="dashboard-grid">
      <div className="card">
        <div className="section-heading"><div><h2>System health</h2><p className="muted">Current infrastructure readiness.</p></div></div>
        <div className="health-grid">
          <HealthIndicator label="API" status="healthy" detail="Reachable" />
          <HealthIndicator label="Database" status={ready?.database || ready?.postgresql || "healthy"} />
          <HealthIndicator label="Redis" status={ready?.redis || "healthy"} />
          <HealthIndicator label="Scheduler" status={ready?.scheduler || "healthy"} />
          <HealthIndicator label="Workers" status={Number(stats.offline_workers || 0) > 0 ? "offline" : "healthy"} detail={`${stats.active_workers ?? 0} active`} />
        </div>
      </div>
      <div className="card">
        <div className="section-heading"><div><h2>Recent jobs</h2><p className="muted">Latest activity across the cluster.</p></div><Link to="/jobs">View all</Link></div>
        {recentJobs.length ? <div className="compact-list">{recentJobs.map((job) => <Link className="compact-row" key={job.id} to={`/jobs/${job.id}`}><span className="mono">{shortId(job.id)}</span><span>{job.queue_name || shortId(job.queue_id)}</span><StatusBadge status={job.status} /><span className="muted">{formatDate(job.created_at)}</span></Link>)}</div> : <p className="muted">No recent jobs.</p>}
      </div>
    </section>

    <section className="chart-grid">
      <ChartCard title="Jobs processed" data={jobsOverTime}><LineChart data={jobsOverTime}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="label" /><YAxis /><Tooltip /><Line type="monotone" dataKey="completed" stroke="#15803d" dot={false} /><Line type="monotone" dataKey="failed" stroke="#b91c1c" dot={false} /></LineChart></ChartCard>
      <ChartCard title="Success / failure" data={successFailure}><BarChart data={successFailure}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#2563eb" /></BarChart></ChartCard>
      <ChartCard title="Queue depth" data={queueDepth}><BarChart data={queueDepth}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="queued" fill="#1d4ed8" /></BarChart></ChartCard>
      <ChartCard title="Worker utilization" data={workerUtil}><BarChart data={workerUtil}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="running" fill="#0f766e" /></BarChart></ChartCard>
    </section>
  </div>;
}

function ChartCard({ title, data, children }) {
  return <div className="card chart-card"><h2>{title}</h2>{data?.length ? <ResponsiveContainer width="100%" height={230}>{children}</ResponsiveContainer> : <p className="muted chart-empty">No series data yet.</p>}</div>;
}
