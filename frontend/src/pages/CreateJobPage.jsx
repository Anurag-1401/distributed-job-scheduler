import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { ErrorState } from "../components/Feedback";
import { listQueues } from "../services/queueService";
import { createJob, createJobBatch } from "../services/jobService";
import { getErrorMessage } from "../utils/errors";
import { useToast } from "../context/ToastContext";
import { unwrapList } from "../utils/format";

export function CreateJobPage() {
  const navigate = useNavigate();
  const { push } = useToast();
  const [type, setType] = useState("IMMEDIATE");
  const [queues, setQueues] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    queue_id: "",
    payload: '{"task":"echo","message":"hello"}',
    priority: 0,
    delay_seconds: 30,
    scheduled_at: "",
    cron_expression: "*/5 * * * *",
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
    batch_payloads: '[{"task":"echo","message":"a"},{"task":"echo","message":"b"}]',
    idempotency_key: "",
  });

  useEffect(() => {
    listQueues({ limit: 100 })
      .then((data) => setQueues(unwrapList(data).items))
      .catch((err) => setError(getErrorMessage(err)));
  }, []);

  function validateCron(value) {
    const fields = value.trim().split(/\s+/);
    if (fields.length !== 5) throw new Error("Cron expression must contain 5 fields");
  }

  function parsePayload(raw) {
    try {
      return JSON.parse(raw);
    } catch {
      throw new Error("Payload must be valid JSON");
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      if (type === "BATCH") {
        const jobs = parsePayload(form.batch_payloads);
        if (!Array.isArray(jobs)) {
          throw new Error("Batch payload must be a JSON array");
        }
        const created = await createJobBatch({
          queue_id: form.queue_id,
          priority: Number(form.priority),
          jobs,
        });
        navigate(created.id ? `/jobs/${created.id}` : "/jobs");
        return;
      }
      const payload = parsePayload(form.payload);
      const body = {
        queue_id: form.queue_id,
        type,
        payload,
        priority: Number(form.priority),
      };
      if (type === "DELAYED") {
        const delay = Number(form.delay_seconds);
        if (!Number.isFinite(delay) || delay < 1) throw new Error("Delay must be at least 1 second");
        body.delay_seconds = delay;
      }
      if (type === "SCHEDULED") {
        const scheduled = new Date(form.scheduled_at);
        if (!form.scheduled_at || Number.isNaN(scheduled.getTime())) throw new Error("Choose a valid scheduled time");
        if (scheduled.getTime() <= Date.now()) throw new Error("Scheduled time must be in the future");
        body.scheduled_at = scheduled.toISOString();
      }
      if (type === "CRON") {
        validateCron(form.cron_expression);
        body.cron_expression = form.cron_expression;
        body.timezone = form.timezone;
      }
      const created = await createJob(body, form.idempotency_key || undefined);
      push("Job created successfully");
      navigate(`/jobs/${created.id}`);
    } catch (err) {
      setError(getErrorMessage(err, err.message));
    }
  }

  return (
    <div>
      <PageHeader title="Create job" subtitle="Task types are validated by the API. Arbitrary Python is never executed from this form." />
      {error ? <ErrorState>{error}</ErrorState> : null}
      <form className="card" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="type">Type</label>
          <select id="type" value={type} onChange={(e) => setType(e.target.value)}>
            <option value="IMMEDIATE">Immediate</option>
            <option value="DELAYED">Delayed</option>
            <option value="SCHEDULED">Scheduled</option>
            <option value="CRON">Recurring (cron)</option>
            <option value="BATCH">Batch</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="queue_id">Queue</label>
          <select id="queue_id" value={form.queue_id} onChange={(e) => setForm({ ...form, queue_id: e.target.value })} required>
            <option value="">Select…</option>
            {queues.map((q) => (
              <option key={q.id} value={q.id}>
                {q.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="priority">Priority</label>
          <input id="priority" type="number" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })} />
        </div>
        {type !== "BATCH" ? (
          <div className="field">
            <label htmlFor="payload">Payload (JSON)</label>
            <textarea id="payload" rows={6} value={form.payload} onChange={(e) => setForm({ ...form, payload: e.target.value })} />
          </div>
        ) : (
          <div className="field">
            <label htmlFor="batch_payloads">Batch jobs (JSON array)</label>
            <textarea id="batch_payloads" rows={8} value={form.batch_payloads} onChange={(e) => setForm({ ...form, batch_payloads: e.target.value })} />
          </div>
        )}
        {type === "DELAYED" ? (
          <div className="field">
            <label htmlFor="delay_seconds">Delay (seconds)</label>
            <input id="delay_seconds" type="number" min="1" value={form.delay_seconds} onChange={(e) => setForm({ ...form, delay_seconds: e.target.value })} />
          </div>
        ) : null}
        {type === "SCHEDULED" ? (
          <div className="field">
            <label htmlFor="scheduled_at">Scheduled time (local, sent as UTC)</label>
            <input id="scheduled_at" type="datetime-local" value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })} required />
          </div>
        ) : null}
        {type === "CRON" ? (
          <>
            <div className="field">
              <label htmlFor="cron_expression">Cron expression</label>
              <input id="cron_expression" value={form.cron_expression} onChange={(e) => setForm({ ...form, cron_expression: e.target.value })} />
            </div>
            <div className="field">
              <label htmlFor="timezone">Timezone</label>
              <input id="timezone" value={form.timezone} onChange={(e) => setForm({ ...form, timezone: e.target.value })} required />
              <small className="muted">Schedules are stored and processed consistently by the backend.</small>
            </div>
          </>
        ) : null}
        {type !== "BATCH" ? (
          <div className="field">
            <label htmlFor="idempotency_key">Idempotency key (optional)</label>
            <input id="idempotency_key" value={form.idempotency_key} onChange={(e) => setForm({ ...form, idempotency_key: e.target.value })} />
          </div>
        ) : null}
        <button className="btn" type="submit">
          Create {type === "BATCH" ? "batch" : "job"}
        </button>
      </form>
    </div>
  );
}
