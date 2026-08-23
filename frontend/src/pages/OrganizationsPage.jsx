import { useCallback, useEffect, useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { listOrganizations, createOrganization } from "../services/orgService";
import { getErrorMessage } from "../utils/errors";
import { unwrapList, formatDate } from "../utils/format";
import { useToast } from "../context/ToastContext";

export function OrganizationsPage() {
  const { push } = useToast();
  const [organizations, setOrganizations] = useState([]);
  const [form, setForm] = useState({ name: "", description: "" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setOrganizations(unwrapList(await listOrganizations()).items);
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    try {
      await createOrganization(form);
      setForm({ name: "", description: "" });
      push("Organization created");
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <PageHeader title="Organizations" subtitle="Tenant boundaries for projects, queues, and jobs." />
      {error ? <ErrorState>{error}</ErrorState> : null}
      <form className="card form-grid" onSubmit={submit}>
        <div><h2>Create organization</h2><p className="muted">Keep project access isolated by organization.</p></div>
        <div className="field"><label htmlFor="org-name">Name</label><input id="org-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
        <div className="field"><label htmlFor="org-description">Description</label><input id="org-description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
        <button className="btn" disabled={saving}>{saving ? "Creating…" : "Create organization"}</button>
      </form>
      {loading ? <LoadingState /> : organizations.length === 0 ? <EmptyState title="No organizations">Create your first organization.</EmptyState> : (
        <div className="card table-wrap table-card">
          <table><thead><tr><th>Name</th><th>Description</th><th>Created</th></tr></thead><tbody>
            {organizations.map((org) => <tr key={org.id}><td><strong>{org.name}</strong></td><td>{org.description || "—"}</td><td>{formatDate(org.created_at)}</td></tr>)}
          </tbody></table>
        </div>
      )}
    </div>
  );
}
