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
    const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
  queue_id: "",
  task: "echo",
  message: "hello",
  priority: 15,
  delay_seconds: 30,
  scheduled_at: "",
  cron_expression: "*/5 * * * *",
  timezone:
    Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
  batch_jobs: [
    { task: "echo", message: "a" },
    { task: "echo", message: "b" },
  ],
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

  async function handleSubmit(event) {
  event.preventDefault();
  setError("");
  setSaving(true);

  try {
    if (!form.queue_id) {
      throw new Error("Please select a queue");
    }

    if (type === "BATCH") {
      const jobs = form.batch_jobs.map((job) => ({
        task: job.task,
        message: job.message,
      }));

      const created = await createJobBatch({
        queue_id: form.queue_id,
        priority: Number(form.priority),
        jobs,
      });

      push("Batch created successfully");
      navigate(created.id ? `/jobs/${created.id}` : "/jobs");
      return;
    }

    const payload = {
      task: form.task,
      message: form.message,
    };

    const body = {
      queue_id: form.queue_id,
      type,
      payload,
      priority: Number(form.priority),
    };

    if (type === "DELAYED") {
      const delay = Number(form.delay_seconds);

      if (!Number.isFinite(delay) || delay < 1) {
        throw new Error("Delay must be at least 1 second");
      }

      body.delay_seconds = delay;
    }

    if (type === "SCHEDULED") {
      const scheduled = new Date(form.scheduled_at);

      if (
        !form.scheduled_at ||
        Number.isNaN(scheduled.getTime())
      ) {
        throw new Error("Choose a valid scheduled time");
      }

      if (scheduled.getTime() <= Date.now()) {
        throw new Error("Scheduled time must be in the future");
      }

      body.scheduled_at = scheduled.toISOString();
    }

    if (type === "CRON") {
      validateCron(form.cron_expression);

      body.cron_expression = form.cron_expression;
      body.timezone = form.timezone;
    }

    const created = await createJob(
      body,
      form.idempotency_key || undefined
    );

    push("Job created successfully");
    navigate(`/jobs/${created.id}`);
  } catch (err) {
    setError(getErrorMessage(err, err.message));
  } finally {
    setSaving(false);
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
  <>
    <div className="field">
      <label htmlFor="task">Task</label>
      <input
        id="task"
        type="text"
        value={form.task}
        onChange={(e) =>
          setForm({
            ...form,
            task: e.target.value,
          })
        }
        placeholder="echo"
        required
      />
    </div>

    <div className="field">
      <label htmlFor="message">Message</label>
      <textarea
        id="message"
        rows={4}
        value={form.message}
        onChange={(e) =>
          setForm({
            ...form,
            message: e.target.value,
          })
        }
        placeholder="Enter message"
        required
      />
    </div>
  </>
) : (
  <div className="field">
    <label>Batch jobs</label>

    {form.batch_jobs.map((job, index) => (
      <div
        key={index}
        className="card"
        style={{ marginBottom: "1rem" }}
      >
        <div className="field">
          <label htmlFor={`batch-task-${index}`}>
            Task
          </label>

          <input
            id={`batch-task-${index}`}
            type="text"
            value={job.task}
            onChange={(e) => {
              const batch_jobs = [...form.batch_jobs];

              batch_jobs[index] = {
                ...batch_jobs[index],
                task: e.target.value,
              };

              setForm({
                ...form,
                batch_jobs,
              });
            }}
            placeholder="echo"
            required
          />
        </div>

        <div className="field">
          <label htmlFor={`batch-message-${index}`}>
            Message
          </label>

          <input
            id={`batch-message-${index}`}
            type="text"
            value={job.message}
            onChange={(e) => {
              const batch_jobs = [...form.batch_jobs];

              batch_jobs[index] = {
                ...batch_jobs[index],
                message: e.target.value,
              };

              setForm({
                ...form,
                batch_jobs,
              });
            }}
            placeholder="Enter message"
            required
          />
        </div>

        {form.batch_jobs.length > 1 ? (
          <button
            type="button"
            className="btn btn-danger"
            onClick={() => {
              setForm({
                ...form,
                batch_jobs: form.batch_jobs.filter(
                  (_, i) => i !== index
                ),
              });
            }}
          >
            Remove
          </button>
        ) : null}
      </div>
    ))}

    <button
      type="button"
      className="btn btn-secondary"
      onClick={() => {
        setForm({
          ...form,
          batch_jobs: [
            ...form.batch_jobs,
            {
              task: "echo",
              message: "",
            },
          ],
        });
      }}
    >
      Add another job
    </button>
  </div>
)}

{type === "DELAYED" ? (
  <div className="field">
    <label htmlFor="delay_seconds">
      Delay (seconds)
    </label>

    <input
      id="delay_seconds"
      type="number"
      min="1"
      value={form.delay_seconds}
      onChange={(e) =>
        setForm({
          ...form,
          delay_seconds: e.target.value,
        })
      }
    />
  </div>
) : null}

{type === "SCHEDULED" ? (
  <div className="field">
    <label htmlFor="scheduled_at">
      Scheduled time
    </label>

    <input
      id="scheduled_at"
      type="datetime-local"
      value={form.scheduled_at}
      onChange={(e) =>
        setForm({
          ...form,
          scheduled_at: e.target.value,
        })
      }
      required
    />

    <small className="muted">
      The selected time will be converted to UTC automatically.
    </small>
  </div>
) : null}

{type === "CRON" ? (
  <>
    <div className="field">
      <label htmlFor="cron_expression">
        Recurrence
      </label>

      <input
        id="cron_expression"
        value={form.cron_expression}
        onChange={(e) =>
          setForm({
            ...form,
            cron_expression: e.target.value,
          })
        }
        placeholder="*/5 * * * *"
        required
      />

      <small className="muted">
        Example: */5 * * * * runs every 5 minutes.
      </small>
    </div>

    <div className="field">
      <label htmlFor="timezone">
        Timezone
      </label>

      <input
        id="timezone"
        value={form.timezone}
        onChange={(e) =>
          setForm({
            ...form,
            timezone: e.target.value,
          })
        }
        required
      />
    </div>
  </>
) : null}

{type !== "BATCH" ? (
  <div className="field">
    <label htmlFor="idempotency_key">
      Idempotency key
    </label>

    <input
      id="idempotency_key"
      value={form.idempotency_key}
      onChange={(e) =>
        setForm({
          ...form,
          idempotency_key: e.target.value,
        })
      }
      placeholder="Optional"
    />

    <small className="muted">
      Prevents accidentally creating the same job twice.
    </small>
  </div>
) : null}
        <button className="btn" type="submit" disabled={saving}>
          {saving ? `Creating... ${type === "BATCH" ? "batch" : "job"}` : `Create ${type === "BATCH" ? "batch" : "job"}`}
        </button>
      </form>
    </div>
  );
}
