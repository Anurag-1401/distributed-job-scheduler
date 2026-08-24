import { useCallback, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "../components/Feedback";
import { StatusBadge } from "../components/StatusBadge";
import { Timeline } from "../components/common/Timeline";
import { LogViewer } from "../components/common/LogViewer";
import {
  cancelJob,
  getJob,
  listJobExecutions,
  listJobLogs,
  retryJob,
} from "../services/jobService";
import { retryDeadLetterJob } from "../services/dlqService";
import { getErrorMessage } from "../utils/errors";
import {
  unwrapList,
  formatDate,
  formatDuration,
} from "../utils/format";
import { usePolling } from "../hooks/usePolling";
import { useSettings } from "../context/SettingsContext";
import { useToast } from "../context/ToastContext";

export function JobDetailPage() {
  const { id } = useParams();
  const { pollIntervalMs } = useSettings();
  const { push } = useToast();

  const [job, setJob] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await getJob(id);

      setJob(data);

      const [executionResponse, logResponse] = await Promise.all([
        listJobExecutions(id, { limit: 50 }).catch(() => ({
          items: data.executions || [],
        })),
        listJobLogs(id, { limit: 100 }).catch(() => ({
          items: data.logs || [],
        })),
      ]);

      const executionItems = unwrapList(executionResponse).items;
      const logItems = unwrapList(logResponse).items;

      setExecutions(
        executionItems.length
          ? executionItems
          : data.executions || [],
      );

      setLogs(
        logItems.length
          ? logItems
          : data.logs || [],
      );

      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  usePolling(load, pollIntervalMs, true);

  async function run(action, successMessage) {
    setActionError("");

    try {
      await action();
      push(successMessage);
      await load();
    } catch (err) {
      setActionError(getErrorMessage(err));
    }
  }

  if (loading) {
    return <LoadingState />;
  }

  if (error && !job) {
    return (
      <ErrorState onRetry={load}>
        {error}
      </ErrorState>
    );
  }

  if (!job) {
    return (
      <EmptyState title="Job not found">
        It may have been deleted or is outside your organization.
      </EmptyState>
    );
  }

  const status = String(job.status || "").toUpperCase();

  const payload =
    typeof job.payload === "string"
      ? job.payload
      : JSON.stringify(job.payload ?? {}, null, 2);

  const policy = job.retry_policy || {};

  const canCancel = [
    "QUEUED",
    "SCHEDULED",
    "RETRYING",
    "CLAIMED",
  ].includes(status);

  const jobType =
    job.type ||
    job.job_type ||
    job.task_type ||
    "—";

  const queueName =
    job.queue_name ||
    job.queue?.name ||
    job.queue_id ||
    "—";

  const workerId =
    job.worker_id ||
    job.worker_key ||
    job.worker?.worker_key ||
    job.worker?.id ||
    "—";

  const priority =
    job.priority ??
    job.queue_priority ??
    "—";

  const attempts =
    job.attempts ??
    job.attempt_count ??
    job.retry_count ??
    job.execution_count ??
    0;

  const deadLetterId =
    job.dead_letter_id ||
    job.deadLetterId ||
    job.dlq_id ||
    id;

  return (
    <div>
      <PageHeader
        title="Job detail"
        subtitle={
          <span className="mono">
            {id}
          </span>
        }
        actions={
          <>
            {status !== "COMPLETED" &&
            status !== "RUNNING" ? (
              <button
                className="btn"
                onClick={() =>
                  run(
                    () => retryJob(id),
                    "Job retry scheduled",
                  )
                }
              >
                Retry
              </button>
            ) : null}

            {status === "DEAD_LETTER" ? (
              <button
                className="btn btn-secondary"
                onClick={() =>
                  run(
                    () => retryDeadLetterJob(deadLetterId),
                    "Job moved back to the queue",
                  )
                }
              >
                Retry from DLQ
              </button>
            ) : null}

            {canCancel ? (
              <button
                className="btn btn-danger"
                onClick={() =>
                  run(
                    () => cancelJob(id),
                    "Job cancelled",
                  )
                }
              >
                Cancel
              </button>
            ) : null}
          </>
        }
      />

      {actionError ? (
        <ErrorState title="Action failed">
          {actionError}
        </ErrorState>
      ) : null}

      {error ? (
        <ErrorState title="Refresh failed">
          {error}
        </ErrorState>
      ) : null}

      <section className="detail-grid">
        <div className="card">
          <div className="detail-header">
            <div>
              <StatusBadge status={job.status} />
              <h2>{jobType}</h2>
            </div>

            <Link to={`/queues/${job.queue_id}`}>
              {queueName}
            </Link>
          </div>

          <dl className="detail-list">
            <div>
              <dt>Priority</dt>
              <dd>{priority}</dd>
            </div>

            <div>
              <dt>Attempts</dt>
              <dd>{attempts}</dd>
            </div>

            <div>
              <dt>Worker</dt>
              <dd className="mono">
                {workerId}
              </dd>
            </div>

            <div>
              <dt>Created</dt>
              <dd>
                {formatDate(job.created_at)}
              </dd>
            </div>

            <div>
              <dt>Scheduled</dt>
              <dd>
                {formatDate(job.scheduled_at)}
              </dd>
            </div>

            <div>
              <dt>Claimed</dt>
              <dd>
                {formatDate(job.claimed_at)}
              </dd>
            </div>

            <div>
              <dt>Started</dt>
              <dd>
                {formatDate(
                  job.started_at ||
                    job.execution_started_at,
                )}
              </dd>
            </div>

            <div>
              <dt>Completed</dt>
              <dd>
                {formatDate(
                  job.completed_at ||
                    job.finished_at,
                )}
              </dd>
            </div>

            <div>
              <dt>Retry policy</dt>
              <dd>
                {policy.strategy || "—"}
                {" · "}
                max {policy.max_attempts ?? "—"}
              </dd>
            </div>

            <div>
              <dt>Next retry</dt>
              <dd>
                {formatDate(job.next_retry_at)}
              </dd>
            </div>

            <div>
              <dt>Last error</dt>
              <dd className="error-cell">
                {job.error ||
                  job.error_message ||
                  job.failure_reason ||
                  "—"}
              </dd>
            </div>
          </dl>
        </div>

        <div className="card">
          <h2>Lifecycle</h2>

          <Timeline
            job={job}
            executions={executions}
          />
        </div>
      </section>

      <section className="card section-gap">
        <h2>Payload</h2>

        <pre className="mono code-block">
          {payload}
        </pre>
      </section>

      <section className="card section-gap">
        <h2>Execution history</h2>

        {executions.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Attempt</th>
                  <th>Worker</th>
                  <th>Status</th>
                  <th>Start</th>
                  <th>End</th>
                  <th>Duration</th>
                  <th>Error</th>
                </tr>
              </thead>

              <tbody>
                {executions.map((execution, index) => {
                  const attempt =
                    execution.attempt_number ??
                    execution.attempt ??
                    index + 1;

                  const executionWorker =
                    execution.worker_id ||
                    execution.worker_key ||
                    execution.worker?.worker_key ||
                    "—";

                  const start =
                    execution.started_at ||
                    execution.start_time;

                  const end =
                    execution.completed_at ||
                    execution.finished_at ||
                    execution.end_time;

                  const duration =
                    execution.duration_ms ??
                    execution.duration ??
                    null;

                  const executionError =
                    execution.error ||
                    execution.error_message ||
                    execution.failure_reason ||
                    "—";

                  return (
                    <tr
                      key={
                        execution.id ||
                        `${attempt}-${start || index}`
                      }
                    >
                      <td>
                        {attempt}
                      </td>

                      <td className="mono">
                        {executionWorker}
                      </td>

                      <td>
                        <StatusBadge
                          status={execution.status}
                        />
                      </td>

                      <td>
                        {formatDate(start)}
                      </td>

                      <td>
                        {formatDate(end)}
                      </td>

                      <td>
                        {duration !== null
                          ? formatDuration(duration)
                          : "—"}
                      </td>

                      <td className="error-cell">
                        {executionError}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="muted">
            No execution attempts recorded.
          </p>
        )}
      </section>

      <section className="card">
        <h2>Execution logs</h2>

        <LogViewer logs={logs} />
      </section>
    </div>
  );
}