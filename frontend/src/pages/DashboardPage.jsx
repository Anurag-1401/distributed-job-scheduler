import { useCallback, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar,
} from "recharts";
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

function firstDefined(obj, keys, fallback = 0) {
  for (const key of keys) {
    const value = obj?.[key];

    if (value !== undefined && value !== null && value !== "") {
      return value;
    }
  }

  return fallback;
}


function normalizeJobsOverTime(data) {
  if (!Array.isArray(data)) {
    return [];
  }

  return data.map((item, index) => ({
    label:
      item.label ??
      item.time ??
      item.timestamp ??
      item.date ??
      item.period ??
      `#${index + 1}`,

    completed: Number(
      firstDefined(item, [
        "completed",
        "completed_jobs",
        "success",
        "successful",
        "success_count",
      ])
    ),

    failed: Number(
      firstDefined(item, [
        "failed",
        "failed_jobs",
        "failure",
        "failures",
        "failure_count",
      ])
    ),
  }));
}


function normalizeSuccessFailure(stats) {
  const source =
    stats?.success_failure ??
    stats?.successFailure ??
    stats?.success_failure_series;

  if (Array.isArray(source) && source.length > 0) {
    return source.map((item) => ({
      name:
        item.name ??
        item.label ??
        item.status ??
        "Unknown",

      value: Number(
        firstDefined(item, [
          "value",
          "count",
          "total",
          "jobs",
        ])
      ),
    }));
  }

  return [
    {
      name: "Completed",
      value: Number(
        firstDefined(stats, [
          "completed_jobs",
          "completed",
          "successful_jobs",
          "success_count",
        ])
      ),
    },
    {
      name: "Failed",
      value: Number(
        firstDefined(stats, [
          "failed_jobs",
          "failed",
          "failure_count",
          "failures",
        ])
      ),
    },
  ];
}


function normalizeQueueDepth(data) {
  if (!Array.isArray(data)) {
    return [];
  }

  return data.map((item, index) => ({
    name:
      item.name ??
      item.queue_name ??
      item.queue ??
      item.label ??
      shortId(item.queue_id) ??
      `Queue ${index + 1}`,

    queued: Number(
      firstDefined(item, [
        "queued",
        "queue_depth",
        "depth",
        "queued_jobs",
        "pending",
        "pending_jobs",
        "count",
        "value",
      ])
    ),
  }));
}


function normalizeWorkerUtilization(data) {
  if (!Array.isArray(data)) {
    return [];
  }

  return data.map((item, index) => ({
    name:
      item.name ??
      item.worker_name ??
      item.worker_key ??
      item.worker ??
      item.label ??
      `Worker ${index + 1}`,

    running: Number(
      firstDefined(item, [
        "running",
        "running_jobs",
        "current_job_count",
        "current_jobs",
        "active_jobs",
        "jobs",
        "value",
      ])
    ),

    capacity: Number(
      firstDefined(item, [
        "capacity",
        "max_concurrency",
        "max_jobs",
      ])
    ),
  }));
}

export function DashboardPage() {
  const { pollIntervalMs } = useSettings();

  const [stats, setStats] = useState(null);
  const [ready, setReady] = useState(null);
  const [recentJobs, setRecentJobs] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  const load = useCallback(async () => {
    try {
      const [overview, health, jobs] = await Promise.all([
        getStats(),

        getReady().catch(() => null),

        listJobs({
          page: 1,
          limit: 8,
          sort: "created_at",
          order: "desc",
        }).catch(() => ({
          items: [],
        })),
      ]);

      setStats(overview);
      setReady(health);
      setRecentJobs(unwrapList(jobs).items);
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);


  usePolling(load, pollIntervalMs, true);


  if (loading) {
    return <LoadingState message="Loading system health…" />;
  }


  if (error && !stats) {
    return (
      <ErrorState onRetry={load}>
        {error}
      </ErrorState>
    );
  }


  if (!stats) {
    return (
      <ErrorState>
        No metrics payload was returned.
      </ErrorState>
    );
  }

  const jobsOverTime = normalizeJobsOverTime(
    stats.jobs_over_time ??
      stats.jobsOverTime ??
      stats.throughput_series ??
      stats.throughputSeries ??
      []
  );


  const queueDepth = normalizeQueueDepth(
    stats.queue_depth ??
      stats.queueDepth ??
      stats.queue_depth_series ??
      []
  );


  const workerUtil = normalizeWorkerUtilization(
    stats.worker_utilization ??
      stats.workerUtilization ??
      stats.worker_utilization_series ??
      []
  );


  const successFailure = normalizeSuccessFailure(stats);

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Operational view of queues, workers, throughput, and failures."
        actions={
          <Link className="btn" to="/jobs/new">
            Create job
          </Link>
        }
      />


      {error ? (
        <ErrorState title="Live refresh failed">
          {error}
        </ErrorState>
      ) : null}

      <section className="stat-grid">
        <StatCard
          label="Queues"
          value={stats.total_queues ?? 0}
        />

        <StatCard
          label="Queued jobs"
          value={stats.queued_jobs ?? 0}
        />

        <StatCard
          label="Running jobs"
          value={stats.running_jobs ?? 0}
        />

        <StatCard
          label="Completed"
          value={stats.completed_jobs ?? 0}
        />

        <StatCard
          label="Failed"
          value={stats.failed_jobs ?? 0}
        />

        <StatCard
          label="DLQ"
          value={stats.dlq_jobs ?? 0}
        />

        <StatCard
          label="Active workers"
          value={stats.active_workers ?? 0}
        />

        <StatCard
          label="Throughput"
          value={stats.throughput ?? 0}
        />
      </section>

      <section className="dashboard-grid">

        <div className="card">
          <div className="section-heading">
            <div>
              <h2>System health</h2>
              <p className="muted">
                Current infrastructure readiness.
              </p>
            </div>
          </div>


          <div className="health-grid">

            <HealthIndicator
              label="API"
              status="healthy"
              detail="Reachable"
            />

            <HealthIndicator
              label="Database"
              status={
                ready?.database ??
                ready?.postgresql ??
                "healthy"
              }
            />

            <HealthIndicator
              label="Redis"
              status={
                ready?.redis ??
                "healthy"
              }
            />

            <HealthIndicator
              label="Scheduler"
              status={
                ready?.scheduler ??
                "healthy"
              }
            />

            <HealthIndicator
              label="Workers"
              status={
                Number(stats.offline_workers ?? 0) > 0
                  ? "offline"
                  : "healthy"
              }
              detail={`${stats.active_workers ?? 0} active`}
            />

          </div>
        </div>


        <div className="card">

          <div className="section-heading">
            <div>
              <h2>Recent jobs</h2>

              <p className="muted">
                Latest activity across the cluster.
              </p>
            </div>

            <Link to="/jobs">
              View all
            </Link>
          </div>


          {recentJobs.length ? (
            <div className="compact-list">

              {recentJobs.map((job) => (
                <Link
                  className="compact-row"
                  key={job.id}
                  to={`/jobs/${job.id}`}
                >
                  <span className="mono">
                    {shortId(job.id)}
                  </span>

                  <span>
                    {job.queue_name ||
                      shortId(job.queue_id)}
                  </span>

                  <StatusBadge status={job.status} />

                  <span className="muted">
                    {formatDate(job.created_at)}
                  </span>
                </Link>
              ))}

            </div>
          ) : (
            <p className="muted">
              No recent jobs.
            </p>
          )}

        </div>

      </section>

      <section className="chart-grid">

        {/* Jobs processed */}

        <ChartCard
          title="Jobs processed"
          data={jobsOverTime}
        >
          <LineChart data={jobsOverTime}>

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="label"
            />

            <YAxis
              allowDecimals={false}
            />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="completed"
              name="Completed"
              stroke="#15803d"
              strokeWidth={2}
              dot={false}
            />

            <Line
              type="monotone"
              dataKey="failed"
              name="Failed"
              stroke="#b91c1c"
              strokeWidth={2}
              dot={false}
            />

          </LineChart>
        </ChartCard>


        {/* Success / Failure */}

        <ChartCard
          title="Success / failure"
          data={successFailure}
        >
          <BarChart data={successFailure}>

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="name"
            />

            <YAxis
              allowDecimals={false}
            />

            <Tooltip />

            <Bar
              dataKey="value"
              name="Jobs"
              fill="#2563eb"
              radius={[4, 4, 0, 0]}
            />

          </BarChart>
        </ChartCard>


        {/* Queue Depth */}

    <ChartCard title="Queue depth" data={queueDepth}>
  <BarChart data={queueDepth}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="name" />
    <YAxis allowDecimals={false} />
    <Tooltip />
    <Bar
      dataKey="queued"
      fill="#1d4ed8"
      minPointSize={6}
    />
  </BarChart>
</ChartCard>

<ChartCard title="Worker utilization" data={workerUtil}>
  <BarChart data={workerUtil}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="name" />
    <YAxis
      domain={[0, 100]}
      allowDecimals={false}
    />
    <Tooltip />
    <Bar
      dataKey="utilization"
      name="Utilization"
      fill="#0f766e"
      minPointSize={6}
      radius={[4, 4, 0, 0]}
    />
  </BarChart>
</ChartCard>

      </section>
    </div>
  );
}

function ChartCard({
  title,
  data,
  children,
}) {
  return (
    <div className="card chart-card">

      <h2>{title}</h2>

      {Array.isArray(data) && data.length > 0 ? (
        <ResponsiveContainer
          width="100%"
          height={230}
        >
          {children}
        </ResponsiveContainer>
      ) : (
        <p className="muted chart-empty">
          No series data yet.
        </p>
      )}

    </div>
  );
}