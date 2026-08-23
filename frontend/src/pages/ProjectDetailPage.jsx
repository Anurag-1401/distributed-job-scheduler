import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { StatCard } from "../components/StatCard";
import { getProject, updateProject, deleteProject } from "../services/projectService";
import { listQueues } from "../services/queueService";
import { getErrorMessage } from "../utils/errors";
import { unwrapList, formatDate } from "../utils/format";
import { StatusBadge } from "../components/StatusBadge";
import { ConfirmDialog } from "../components/common/ConfirmDialog";
import { useToast } from "../context/ToastContext";

export function ProjectDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { push } = useToast();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [project, setProject] = useState(null);
  const [queues, setQueues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getProject(id);
      setProject(data);
      setName(data.name || "");
      setDescription(data.description || "");
      const q = await listQueues({ project_id: id, limit: 50 });
      setQueues(unwrapList(q).items);
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSave(event) {
    event.preventDefault();
    try {
      await updateProject(id, { name, description });
      push("Project updated");
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function handleDelete() {
    try {
      await deleteProject(id);
      push("Project deleted");
      navigate("/projects");
    } catch (err) { setError(getErrorMessage(err)); }
  }

  if (loading) {
    return <LoadingState />;
  }
  if (error && !project) {
    return <ErrorState>{error}</ErrorState>;
  }
  if (!project) {
    return <EmptyState title="Project not found">Check the ID or your organization access.</EmptyState>;
  }

  const counts = project.job_counts || {};

  return (
    <div>
      <PageHeader
        title={project.name}
        subtitle={`Created ${formatDate(project.created_at)}`}
        actions={
          <button type="button" className="btn btn-danger" onClick={() => setConfirmDelete(true)}>
            Delete
          </button>
        }
      />
      {error ? <ErrorState>{error}</ErrorState> : null}
      <section className="stat-grid">
        <StatCard label="Queued" value={counts.queued} />
        <StatCard label="Running" value={counts.running} />
        <StatCard label="Completed" value={counts.completed} />
        <StatCard label="Failed" value={counts.failed} />
      </section>
      <form className="card" onSubmit={handleSave} style={{ marginBottom: "1rem" }}>
        <h2>Edit project</h2>
        <div className="field">
          <label htmlFor="name">Name</label>
          <input id="name" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="description">Description</label>
          <textarea id="description" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>
        <p className="muted">Organization: {project.organization_id}</p>
        <button className="btn" type="submit">
          Save
        </button>
      </form>
      <div className="card">
        <h2>Queues</h2>
        {queues.length === 0 ? (
          <p className="muted">No queues in this project.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Concurrency</th>
                  <th>Priority</th>
                </tr>
              </thead>
              <tbody>
                {queues.map((queue) => (
                  <tr key={queue.id}>
                    <td>
                      <Link to={`/queues/${queue.id}`}>{queue.name}</Link>
                    </td>
                    <td>
                      <StatusBadge status={queue.status} />
                    </td>
                    <td>{queue.concurrency_limit}</td>
                    <td>{queue.priority}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <ConfirmDialog open={confirmDelete} title="Delete project?" message="This removes the project and its queue configuration." confirmLabel="Delete project" danger onCancel={() => setConfirmDelete(false)} onConfirm={handleDelete} />
    </div>
  );
}
