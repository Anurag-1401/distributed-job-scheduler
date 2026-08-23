import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { Pagination } from "../components/Pagination";
import { StatusBadge } from "../components/StatusBadge";
import { createQueue, listQueues, pauseQueue, resumeQueue } from "../services/queueService";
import { listProjects } from "../services/projectService";
import { getErrorMessage } from "../utils/errors";
import { unwrapList } from "../utils/format";
import { usePolling } from "../hooks/usePolling";
import { useSettings } from "../context/SettingsContext";

const EMPTY_FORM = {
  project_id: "",
  name: "",
  priority: 0,
  concurrency_limit: 5,
  strategy: "EXPONENTIAL",
  max_attempts: 5,
  base_delay_seconds: 2,
  max_delay_seconds: 60,
  jitter: true,
};

export function QueuesPage() {
  const { pollIntervalMs } = useSettings();
  const [page, setPage] = useState(1);
  const [list, setList] = useState({ items: [], total: 0 });
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);

  const load = useCallback(async () => {
    try {
      const [queues, projectData] = await Promise.all([listQueues({ page, limit: 20 }), listProjects({ limit: 100 }).catch(() => ({ items: [] }))]);
      setList(unwrapList(queues));
      setProjects(unwrapList(projectData).items);
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    setLoading(true);
  }, [page]);

  usePolling(load, pollIntervalMs, true);

  async function handleCreate(event) {
    event.preventDefault();
    try {
      await createQueue({
        project_id: form.project_id,
        name: form.name,
        priority: Number(form.priority),
        concurrency_limit: Number(form.concurrency_limit),
        retry_policy: {
          strategy: form.strategy,
          max_attempts: Number(form.max_attempts),
          base_delay_seconds: Number(form.base_delay_seconds),
          max_delay_seconds: Number(form.max_delay_seconds),
          jitter: Boolean(form.jitter),
        },
      });
      setForm(EMPTY_FORM);
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function toggle(queue) {
    try {
      if (String(queue.status).toUpperCase() === "PAUSED") {
        await resumeQueue(queue.id);
      } else {
        await pauseQueue(queue.id);
      }
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader title="Queues" subtitle="Pause and resume without deleting configuration." />
      <form className="card" onSubmit={handleCreate} style={{ marginBottom: "1rem" }}>
        <h2>Create queue</h2>
        <div className="filters">
          <div className="field">
            <label htmlFor="project_id">Project</label>
            <select id="project_id" value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })} required>
              <option value="">Select…</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="qname">Name</label>
            <input id="qname" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div className="field">
            <label htmlFor="priority">Priority</label>
            <input id="priority" type="number" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })} />
          </div>
          <div className="field">
            <label htmlFor="concurrency_limit">Concurrency</label>
            <input
              id="concurrency_limit"
              type="number"
              min="1"
              value={form.concurrency_limit}
              onChange={(e) => setForm({ ...form, concurrency_limit: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="strategy">Retry strategy</label>
            <select id="strategy" value={form.strategy} onChange={(e) => setForm({ ...form, strategy: e.target.value })}>
              <option>FIXED</option><option>LINEAR</option><option>EXPONENTIAL</option>
            </select>
          </div>
          <div className="field"><label htmlFor="max_attempts">Max attempts</label><input id="max_attempts" type="number" min="1" value={form.max_attempts} onChange={(e) => setForm({ ...form, max_attempts: e.target.value })} /></div>
          <div className="field"><label htmlFor="base_delay_seconds">Base delay (seconds)</label><input id="base_delay_seconds" type="number" min="0" value={form.base_delay_seconds} onChange={(e) => setForm({ ...form, base_delay_seconds: e.target.value })} /></div>
          <div className="field"><label htmlFor="max_delay_seconds">Max delay (seconds)</label><input id="max_delay_seconds" type="number" min="0" value={form.max_delay_seconds} onChange={(e) => setForm({ ...form, max_delay_seconds: e.target.value })} /></div>
          <label className="checkbox-field"><input type="checkbox" checked={form.jitter} onChange={(e) => setForm({ ...form, jitter: e.target.checked })} /> Enable retry jitter</label>
        </div>
        <button className="btn" type="submit">
          Create queue
        </button>
      </form>
      {error ? <ErrorState>{error}</ErrorState> : null}
      {loading ? <LoadingState /> : null}
      {!loading && list.items.length === 0 ? <EmptyState title="No queues">Create a queue to accept jobs.</EmptyState> : null}
      {list.items.length > 0 ? (
        <div className="table-wrap card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Concurrency</th>
                <th>Priority</th>
                <th>Queued</th>
                <th>Running</th>
                <th>Completed</th>
                <th>Failed</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {list.items.map((queue) => {
                const s = queue.stats || queue;
                return (
                  <tr key={queue.id}>
                    <td>
                      <Link to={`/queues/${queue.id}`}>{queue.name}</Link>
                    </td>
                    <td>
                      <StatusBadge status={queue.status} />
                    </td>
                    <td>{queue.concurrency_limit}</td>
                    <td>{queue.priority}</td>
                    <td>{s.queued_jobs ?? s.queued ?? "—"}</td>
                    <td>{s.running_jobs ?? s.running ?? "—"}</td>
                    <td>{s.completed_jobs ?? s.completed ?? "—"}</td>
                    <td>{s.failed_jobs ?? s.failed ?? "—"}</td>
                    <td className="row-actions">
                      <button type="button" className="btn btn-secondary" onClick={() => toggle(queue)}>
                        {String(queue.status).toUpperCase() === "PAUSED" ? "Resume" : "Pause"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}
      <Pagination page={page} limit={20} total={list.total} onPageChange={setPage} />
    </div>
  );
}
