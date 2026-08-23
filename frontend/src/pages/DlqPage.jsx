import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { Pagination } from "../components/Pagination";
import { deleteDeadLetterJob, listDeadLetterJobs, retryDeadLetterJob } from "../services/dlqService";
import { getErrorMessage } from "../utils/errors";
import { ConfirmDialog } from "../components/common/ConfirmDialog";
import { useToast } from "../context/ToastContext";
import { unwrapList, formatDate, shortId } from "../utils/format";

export function DlqPage() {
  const [page, setPage] = useState(1);
  const [list, setList] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { push } = useToast();
  const [pendingDelete, setPendingDelete] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setList(unwrapList(await listDeadLetterJobs({ page, limit: 20 })));
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    load();
  }, [load]);

  async function retry(id) {
    try {
      await retryDeadLetterJob(id);
      push("Job moved back to the queue");
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function remove(id) {
    try {
      await deleteDeadLetterJob(id);
      push("DLQ record removed");
      setPendingDelete(null);
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader title="Dead letter queue" subtitle="Jobs that exhausted retries." />
      {error ? <ErrorState>{error}</ErrorState> : null}
      {loading ? <LoadingState /> : null}
      {!loading && list.items.length === 0 ? <EmptyState title="DLQ is empty">Failed jobs with remaining retries will not appear here.</EmptyState> : null}
      {list.items.length > 0 ? (
        <div className="table-wrap card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Job</th>
                <th>Queue</th>
                <th>Error</th>
                <th>Attempts</th>
                <th>Last failure</th>
                <th>Worker</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {list.items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <Link className="mono" to={`/jobs/${item.job_id || item.id}`}>
                      {shortId(item.job_id || item.id)}
                    </Link>
                  </td>
                  <td>{item.queue_name || shortId(item.queue_id)}</td>
                  <td>{item.final_error || item.failure_reason || item.error}</td>
                  <td>{item.attempts}</td>
                  <td>{formatDate(item.last_failed_at || item.updated_at)}</td>
                  <td className="mono">{shortId(item.worker_id)}</td>
                  <td>{formatDate(item.created_at)}</td>
                  <td className="row-actions">
                    <Link to={`/jobs/${item.job_id || item.id}`}>Inspect</Link>
                    <button type="button" className="btn" onClick={() => retry(item.id)}>
                      Retry
                    </button>
                    <button type="button" className="btn btn-secondary" onClick={() => setPendingDelete(item)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <Pagination page={page} limit={20} total={list.total} onPageChange={setPage} />
      <ConfirmDialog open={Boolean(pendingDelete)} title="Remove DLQ record?" message="This removes the DLQ record from the operational view. The original job remains inspectable by its job ID." confirmLabel="Remove" danger onCancel={() => setPendingDelete(null)} onConfirm={() => remove(pendingDelete.id)} />
    </div>
  );
}
