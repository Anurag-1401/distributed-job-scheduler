import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { Pagination } from "../components/Pagination";
import { StatusBadge } from "../components/StatusBadge";
import { listJobs } from "../services/jobService";
import { getErrorMessage } from "../utils/errors";
import { unwrapList, formatDate, formatDuration, shortId } from "../utils/format";
import { useDebounce } from "../hooks/useDebounce";
import { usePolling } from "../hooks/usePolling";
import { useSettings } from "../context/SettingsContext";

const STATUSES = ["", "SCHEDULED", "QUEUED", "CLAIMED", "RUNNING", "COMPLETED", "FAILED", "RETRYING", "CANCELLED", "DEAD_LETTER"];

export function JobsPage() {
  const { pollIntervalMs } = useSettings();
  const [filters, setFilters] = useState({
    status: "",
    queue_id: "",
    priority: "",
    worker_id: "",
    created_after: "",
    created_before: "",
    q: "",
    sort: "created_at",
    order: "desc",
    page: 1,
    limit: 20,
  });
  const debouncedSearch = useDebounce(filters.q, 400);
  const [list, setList] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await listJobs({ ...filters, q: debouncedSearch });
      setList(unwrapList(data));
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [filters, debouncedSearch]);

  usePolling(load, pollIntervalMs, true);

  function update(key, value) {
    setFilters((prev) => ({ ...prev, page: 1, [key]: value }));
  }

  return (
    <div>
      <PageHeader
        title="Jobs"
        subtitle="Paginated explorer. Search is debounced."
        actions={
          <Link className="btn" to="/jobs/new">
            Create job
          </Link>
        }
      />
      <div className="filters">
        <div className="field">
          <label htmlFor="q">Search</label>
          <input id="q" value={filters.q} onChange={(e) => update("q", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="status">Status</label>
          <select id="status" value={filters.status} onChange={(e) => update("status", e.target.value)}>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s || "Any"}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="queue_id">Queue ID</label>
          <input id="queue_id" value={filters.queue_id} onChange={(e) => update("queue_id", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="priority">Priority</label>
          <input id="priority" value={filters.priority} onChange={(e) => update("priority", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="worker_id">Worker ID</label>
          <input id="worker_id" value={filters.worker_id} onChange={(e) => update("worker_id", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="created_after">Created after</label>
          <input id="created_after" type="datetime-local" value={filters.created_after} onChange={(e) => update("created_after", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="created_before">Created before</label>
          <input id="created_before" type="datetime-local" value={filters.created_before} onChange={(e) => update("created_before", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="sort">Sort</label>
          <select
            id="sort"
            value={`${filters.sort}:${filters.order}`}
            onChange={(e) => {
              const [sort, order] = e.target.value.split(":");
              setFilters((prev) => ({ ...prev, sort, order }));
            }}
          >
            <option value="created_at:desc">Created desc</option>
            <option value="created_at:asc">Created asc</option>
            <option value="priority:desc">Priority desc</option>
            <option value="status:asc">Status</option>
          </select>
        </div>
      </div>
      {error ? <ErrorState>{error}</ErrorState> : null}
      {loading ? <LoadingState /> : null}
      {!loading && list.items.length === 0 ? <EmptyState title="No jobs">Adjust filters or create a job.</EmptyState> : null}
      {list.items.length > 0 ? (
        <div className="table-wrap card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Queue</th>
                <th>Type</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Attempts</th>
                <th>Worker</th>
                <th>Created</th>
                <th>Scheduled</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {list.items.map((job) => (
                <tr key={job.id}>
                  <td>
                    <Link className="mono" to={`/jobs/${job.id}`}>
                      {shortId(job.id)}
                    </Link>
                  </td>
                  <td>{job.queue_name || shortId(job.queue_id)}</td>
                  <td>{job.type || job.job_type}</td>
                  <td>
                    <StatusBadge status={job.status} />
                  </td>
                  <td>{job.priority}</td>
                  <td>{job.attempts ?? job.attempt_count}</td>
                  <td className="mono">{shortId(job.worker_id)}</td>
                  <td>{formatDate(job.created_at)}</td>
                  <td>{formatDate(job.scheduled_at)}</td>
                  <td>{formatDuration(job.duration_ms)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <Pagination page={filters.page} limit={filters.limit} total={list.total} onPageChange={(page) => setFilters((prev) => ({ ...prev, page }))} />
    </div>
  );
}
