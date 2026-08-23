import { useCallback, useState } from "react";
import { Link } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "../components/Feedback";
import { Pagination } from "../components/Pagination";
import { StatusBadge } from "../components/StatusBadge";

import { listWorkers } from "../services/workerService";
import { getErrorMessage } from "../utils/errors";
import {
  unwrapList,
  formatDate,
  shortId,
} from "../utils/format";

import { usePolling } from "../hooks/usePolling";
import { useSettings } from "../context/SettingsContext";

export function WorkersPage() {
  const { pollIntervalMs } = useSettings();

  const [page, setPage] = useState(1);
  const [list, setList] = useState({
    items: [],
    total: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const response = await listWorkers({
        page,
        limit: 20,
      });

      setList(unwrapList(response));
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [page]);

  usePolling(load, pollIntervalMs, true);

  return (
    <div>

      <PageHeader
        title="Workers"
        subtitle="Heartbeat-driven health and distributed execution capacity."
      />

      {error ? (
        <ErrorState onRetry={load}>
          {error}
        </ErrorState>
      ) : null}

      {loading ? <LoadingState /> : null}

      {!loading && list.items.length === 0 ? (
        <EmptyState title="No workers">
          Start a worker process to see it here.
        </EmptyState>
      ) : null}


      {list.items.length > 0 ? (
        <div className="card table-wrap table-card">
          <table>
            <thead>
              <tr>
                <th>Worker</th>
                <th>Status</th>
                <th>Concurrency</th>
                <th>Running</th>
                <th>Utilization</th>
                <th>Heartbeat</th>
                <th>Completed</th>
                <th>Failed</th>
                <th>Uptime</th>
              </tr>
            </thead>

            <tbody>
              {list.items.map((worker) => {
                const workerId =
                  worker.id || worker.worker_id;

                const capacity = Number(
                  worker.concurrency ||
                    worker.capacity ||
                    0
                );

                const running = Number(
                  worker.current_job_count ??
                    worker.running_jobs ??
                    0
                );

                const calculatedUtilization = capacity
                  ? Math.round(
                      (running / capacity) * 100
                    )
                  : null;

                const utilization =
                  worker.utilization ??
                  calculatedUtilization;

                const utilizationValue =
                  Math.min(
                    100,
                    Math.max(
                      0,
                      Number(utilization) || 0
                    )
                  );

                return (
                  <tr key={workerId}>
                    {/* Worker */}
                    <td>
                      <Link
                        className="mono"
                        to={`/workers/${workerId}`}
                      >
                        {shortId(workerId)}
                      </Link>
                    </td>

                    {/* Status */}
                    <td>
                      <StatusBadge
                        status={worker.status}
                      />
                    </td>

                    {/* Concurrency */}
                    <td>
                      {capacity || "—"}
                    </td>

                    {/* Running Jobs */}
                    <td>
                      {running}
                    </td>

                    {/* Utilization */}
                    <td>
                      <div className="util-cell">
                        <div className="util-track">
                          <span
                            style={{
                              width: `${utilizationValue}%`,
                            }}
                          />
                        </div>

                        <span>
                          {utilization == null
                            ? "—"
                            : `${utilization}%`}
                        </span>
                      </div>
                    </td>

                    {/* Heartbeat */}
                    <td>
                      {formatDate(
                        worker.last_heartbeat_at ||
                          worker.last_heartbeat
                      )}
                    </td>

                    {/* Completed */}
                    <td>
                      {worker.completed_jobs ?? "—"}
                    </td>

                    {/* Failed */}
                    <td>
                      {worker.failed_jobs ?? "—"}
                    </td>

                    {/* Uptime */}
                    <td>
                      {worker.uptime || "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}


      <Pagination
        page={page}
        limit={20}
        total={list.total}
        onPageChange={setPage}
      />
    </div>
  );
}