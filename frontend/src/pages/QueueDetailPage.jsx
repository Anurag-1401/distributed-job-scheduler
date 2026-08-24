import { useCallback, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "../components/Feedback";
import { StatCard } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import {
  getQueue,
  pauseQueue,
  resumeQueue,
  updateQueue,
} from "../services/queueService";
import { listJobs } from "../services/jobService";
import { getErrorMessage } from "../utils/errors";
import { unwrapList, formatDate } from "../utils/format";
import { usePolling } from "../hooks/usePolling";
import { useSettings } from "../context/SettingsContext";
import { useToast } from "../context/ToastContext";
import { RETRY_STRATEGIES } from "../constants/retryStrategies";

export function QueueDetailPage() {
  const { id } = useParams();
  const { pollIntervalMs } = useSettings();
  const { push } = useToast();

  const [queue, setQueue] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    concurrency_limit: 1,
    priority: 0,
    strategy: "EXPONENTIAL",
    max_attempts: 5,
    base_delay_seconds: 2,
    max_delay_seconds: 60,
    jitter: true,
  });

  const load = useCallback(async () => {
    try {
      const data = await getQueue(id);

      setQueue(data);

      const policy = data.retry_policy || {};

      setForm({
        concurrency_limit: data.concurrency_limit ?? 1,
        priority: data.priority ?? 0,
        strategy: policy.strategy || "EXPONENTIAL",
        max_attempts: policy.max_attempts ?? 5,
        base_delay_seconds: policy.base_delay_seconds ?? 2,
        max_delay_seconds: policy.max_delay_seconds ?? 60,
        jitter: policy.jitter ?? true,
      });

      const recent = await listJobs({
        queue_id: id,
        limit: 10,
        sort: "created_at",
        order: "desc",
      });

      setJobs(unwrapList(recent).items);
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  usePolling(load, pollIntervalMs, true);

  async function save(event) {
    event.preventDefault();

    try {
      await updateQueue(id, {
        concurrency_limit: Number(form.concurrency_limit),
        priority: Number(form.priority),
        retry_policy: {
          strategy: form.strategy,
          max_attempts: Number(form.max_attempts),
          base_delay_seconds: Number(form.base_delay_seconds),
          max_delay_seconds: Number(form.max_delay_seconds),
          jitter: Boolean(form.jitter),
        },
      });

      push("Queue configuration saved");
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function toggle() {
    try {
      if (String(queue.status).toUpperCase() === "PAUSED") {
        await resumeQueue(id);
        push("Queue resumed");
      } else {
        await pauseQueue(id);
        push("Queue paused");
      }

      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  if (loading) {
    return <LoadingState />;
  }

  if (error && !queue) {
    return (
      <ErrorState onRetry={load}>
        {error}
      </ErrorState>
    );
  }

  if (!queue) {
    return (
      <EmptyState title="Queue not found">
        It may belong to another organization.
      </EmptyState>
    );
  }

  const stats = queue.stats || {};
  const isPaused = String(queue.status).toUpperCase() === "PAUSED";

  return (
    <div>
      <PageHeader
        title={queue.name}
        subtitle={`Project: ${queue.project_name}`}
        actions={
          <button
            className="btn btn-secondary"
            onClick={toggle}
          >
            {isPaused ? "Resume" : "Pause"}
          </button>
        }
      />

      {error ? (
        <ErrorState title="Refresh failed">
          {error}
        </ErrorState>
      ) : null}

      <section className="stat-grid">
        <StatCard label="Status" value={queue.status} />
        <StatCard
          label="Queued"
          value={stats.queued_jobs ?? stats.queued}
        />
        <StatCard
          label="Scheduled"
          value={stats.scheduled_jobs ?? stats.scheduled}
        />
        <StatCard
          label="Running"
          value={stats.running_jobs ?? stats.running}
        />
        <StatCard
          label="Completed"
          value={stats.completed_jobs ?? stats.completed}
        />
        <StatCard
          label="Failed"
          value={stats.failed_jobs ?? stats.failed}
        />
        <StatCard
          label="DLQ"
          value={stats.dlq_jobs ?? stats.dlq}
        />
        <StatCard
          label="Throughput"
          value={stats.throughput}
        />
      </section>

      <form
        className="card section-gap"
        onSubmit={save}
      >
        <div className="section-heading">
          <div>
            <h2>Queue configuration</h2>
            <p className="muted">
              These settings control scheduling and retry behavior.
            </p>
          </div>

          <StatusBadge status={queue.status} />
        </div>

        <div className="form-grid four">
          <div className="field">
            <label>Concurrency limit</label>
            <input
              type="number"
              min="1"
              value={form.concurrency_limit}
              onChange={(e) =>
                setForm({
                  ...form,
                  concurrency_limit: e.target.value,
                })
              }
            />
          </div>

          <div className="field">
            <label>Priority</label>
            <input
              type="number"
              min="1"
              value={form.priority}
              onChange={(e) =>
                setForm({
                  ...form,
                  priority: e.target.value,
                })
              }
            />
          </div>

          <div className="field">
            <label>Retry strategy</label>
            <select
              value={form.strategy}
              onChange={(e) =>
                setForm({
                  ...form,
                  strategy: e.target.value,
                })
              }
            >
              {RETRY_STRATEGIES.map((strategy) => (
                <option key={strategy} value={strategy}>
                  {strategy}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Max attempts</label>
            <input
              type="number"
              min="1"
              value={form.max_attempts}
              onChange={(e) =>
                setForm({
                  ...form,
                  max_attempts: e.target.value,
                })
              }
            />
          </div>

          <div className="field">
            <label>Base delay (seconds)</label>
            <input
              type="number"
              min="0"
              value={form.base_delay_seconds}
              onChange={(e) =>
                setForm({
                  ...form,
                  base_delay_seconds: e.target.value,
                })
              }
            />
          </div>

          <div className="field">
            <label>Max delay (seconds)</label>
            <input
              type="number"
              min="0"
              value={form.max_delay_seconds}
              onChange={(e) =>
                setForm({
                  ...form,
                  max_delay_seconds: e.target.value,
                })
              }
            />
          </div>

          <label className="checkbox-field">
            <input
              type="checkbox"
              checked={form.jitter}
              onChange={(e) =>
                setForm({
                  ...form,
                  jitter: e.target.checked,
                })
              }
            />
            Enable retry jitter
          </label>
        </div>

        <button
          className="btn"
          type="submit"
        >
          Save configuration
        </button>
      </form>

      <section className="card">
        <div className="section-heading">
          <div>
            <h2>Recent jobs</h2>
            <p className="muted">
              Latest jobs in this queue.
            </p>
          </div>

          <Link to="/jobs">Open explorer</Link>
        </div>

        {jobs.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Job</th>
                  <th>Status</th>
                  <th>Type</th>
                  <th>Worker</th>
                  <th>Created</th>
                </tr>
              </thead>

              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id}>
                    <td>
                      <Link
                        className="mono"
                        to={`/jobs/${job.id}`}
                      >
                        {job.id}
                      </Link>
                    </td>

                    <td>
                      <StatusBadge status={job.status} />
                    </td>

                    <td>
                      {job.type || job.job_type}
                    </td>

                    <td className="mono">
                      {job.worker_id || "—"}
                    </td>

                    <td>
                      {formatDate(job.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="muted">No recent jobs.</p>
        )}
      </section>
    </div>
  );
}