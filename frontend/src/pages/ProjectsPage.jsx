import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { Pagination } from "../components/Pagination";
import { createProject, deleteProject, listProjects } from "../services/projectService";
import { listOrganizations } from "../services/orgService";
import { getErrorMessage } from "../utils/errors";
import { ConfirmDialog } from "../components/common/ConfirmDialog";
import { useToast } from "../context/ToastContext";
import { unwrapList, formatDate } from "../utils/format";

export function ProjectsPage() {
  const navigate = useNavigate();
  const { push } = useToast();
  const [pendingDelete, setPendingDelete] = useState(null);
  const [page, setPage] = useState(1);
  const [list, setList] = useState({ items: [], total: 0 });
  const [orgs, setOrgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ name: "", description: "", organization_id: "" });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [projects, organizations] = await Promise.all([listProjects({ page, limit: 20 }), listOrganizations().catch(() => ({ items: [] }))]);
      setList(unwrapList(projects));
      setOrgs(unwrapList(organizations).items);
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

  useEffect(() => {
    console.log("Organizations changed:", orgs);
  }, [orgs]);

  async function handleCreate(event) {
    event.preventDefault();
    setSaving(true);
    try {
      const created = await createProject(form);
      push("Project created");
      navigate(`/projects/${created.id}`);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteProject(id);
      push("Project deleted");
      setPendingDelete(null);
      load();
    } catch (err) { setError(getErrorMessage(err)); }
  }

  return (
    <div>
      <PageHeader title="Projects" subtitle="Projects belong to an organization. Access is isolated per membership." />
      <form className="card" onSubmit={handleCreate} style={{ marginBottom: "1rem" }}>
        <h2>Create project</h2>
        <div className="filters">
          <div className="field">
            <label htmlFor="organization_id">Organization</label>
            <select
              id="organization_id"
              value={form.organization_id}
              onChange={(e) => setForm({ ...form, organization_id: e.target.value })}
              required
            >
              <option value="">Select…</option>
              {orgs.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="name">Name</label>
            <input id="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div className="field">
            <label htmlFor="description">Description</label>
            <input id="description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
        </div>
        <button className="btn" type="submit" disabled={saving}>
          {saving ? `Creating...` : `Create project`}
        </button>
      </form>
      {error ? <ErrorState>{error}</ErrorState> : null}
      {loading ? <LoadingState /> : null}
      {!loading && list.items.length === 0 ? <EmptyState title="No projects">Create a project to start defining queues.</EmptyState> : null}
      {list.items.length > 0 ? (
        <div className="table-wrap card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Organization</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {list.items.map((project) => (
                <tr key={project.id}>
                  <td>
                    <Link to={`/projects/${project.id}`}>{project.name}</Link>
                  </td>
                  <td>{project.organization_name || project.organization_id}</td>
                  <td>{formatDate(project.created_at)}</td>
                  <td className="row-actions">
                    <Link to={`/projects/${project.id}`}>Open</Link>
                    <button type="button" className="btn btn-secondary" onClick={() => setPendingDelete(project)}>
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
      <ConfirmDialog open={Boolean(pendingDelete)} title="Delete project?" message={pendingDelete ? `This will remove ${pendingDelete.name} and its configuration.` : ""} confirmLabel="Delete project" danger onCancel={() => setPendingDelete(null)} onConfirm={() => handleDelete(pendingDelete.id)} />
    </div>
  );
}
