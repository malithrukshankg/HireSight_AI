import { useCallback, useEffect, useState } from "react";
import {
  getOrganizationsForCurrentUser,
  createOrganization,
  updateOrganization,
  deleteOrganization,
} from "../../services/organizationService";
import type { Organization, PlanType } from "../../types/organization";

const PLANS: PlanType[] = ["free", "pro", "enterprise"];

function OrganizationCard({
  org,
  onUpdate,
  onDelete,
  getToken,
}: {
  org: Organization;
  onUpdate: (org: Organization) => void;
  onDelete: (org: Organization) => void;
  getToken: () => Promise<string>;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(org.name);
  const [editPlan, setEditPlan] = useState<PlanType>(org.plan);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleSave = async () => {
    if (editName.trim() === "") return;
    setSaving(true);
    try {
      const token = await getToken();
      const updated = await updateOrganization(token, org.id, {
        name: editName.trim(),
        plan: editPlan,
      });
      onUpdate(updated);
      setIsEditing(false);
    } catch {
      setSaving(false);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditName(org.name);
    setEditPlan(org.plan);
    setIsEditing(false);
  };

  const handleDeleteClick = async () => {
    if (!window.confirm(`Delete organization "${org.name}"?`)) return;
    setDeleting(true);
    try {
      const token = await getToken();
      await deleteOrganization(token, org.id);
      onDelete(org);
    } finally {
      setDeleting(false);
    }
  };

  if (isEditing) {
    return (
      <div className="rounded-xl border border-white/20 bg-white/10 p-4 backdrop-blur-sm">
        <input
          type="text"
          value={editName}
          onChange={(e) => setEditName(e.target.value)}
          className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white placeholder-white/50"
          placeholder="Organization name"
        />
        <select
          value={editPlan}
          onChange={(e) => setEditPlan(e.target.value as PlanType)}
          className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white"
        >
          {PLANS.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleSave}
            disabled={saving || editName.trim() === ""}
            className="rounded-xl bg-accent py-2 px-4 font-medium text-white transition-colors hover:bg-accent-hover disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
          <button
            type="button"
            onClick={handleCancel}
            disabled={saving}
            className="rounded-xl border-2 border-white/50 bg-white/10 py-2 px-4 font-medium text-white transition-colors hover:bg-white/20"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between rounded-xl border border-white/20 bg-white/10 p-4 backdrop-blur-sm">
      <div>
        <p className="font-medium text-white">{org.name}</p>
        <p className="text-sm text-white/80">Plan: {org.plan}</p>
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          disabled={deleting}
          className="rounded-xl border-2 border-white/50 bg-white/10 py-2 px-4 text-sm font-medium text-white transition-colors hover:bg-white/20"
        >
          Edit
        </button>
        <button
          type="button"
          onClick={handleDeleteClick}
          disabled={deleting}
          className="rounded-xl bg-red-500/30 py-2 px-4 text-sm font-medium text-white transition-colors hover:bg-red-500/50"
        >
          {deleting ? "Deleting..." : "Delete"}
        </button>
      </div>
    </div>
  );
}

export type OrganizationsTileProps = {
  getToken: () => Promise<string>;
};

export function OrganizationsTile({ getToken }: OrganizationsTileProps) {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createName, setCreateName] = useState("");
  const [createPlan, setCreatePlan] = useState<PlanType>("free");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const fetchOrganizations = useCallback(async () => {
    try {
      setError(null);
      const token = await getToken();
      const data = await getOrganizationsForCurrentUser(token);
      setOrganizations(data);
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)));
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    fetchOrganizations();
  }, [fetchOrganizations]);

  const handleOrgUpdate = (updated: Organization) => {
    setOrganizations((prev) =>
      prev.map((o) => (o.id === updated.id ? updated : o))
    );
  };

  const handleOrgDelete = (deleted: Organization) => {
    setOrganizations((prev) => prev.filter((o) => o.id !== deleted.id));
  };

  const handleCreate = async () => {
    if (createName.trim() === "") return;
    setCreating(true);
    setCreateError(null);
    try {
      const token = await getToken();
      const created = await createOrganization(token, {
        name: createName.trim(),
        plan: createPlan,
      });
      setOrganizations((prev) => [created, ...prev]);
      setCreateName("");
      setCreatePlan("free");
      setShowCreateForm(false);
    } catch (e) {
      setCreateError(e instanceof Error ? e.message : String(e));
    } finally {
      setCreating(false);
    }
  };

  const handleCancelCreate = () => {
    setShowCreateForm(false);
    setCreateName("");
    setCreatePlan("free");
    setCreateError(null);
  };

  return (
    <div className="rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Organizations</h2>
        {!loading && !error && (
          <button
            type="button"
            onClick={() => setShowCreateForm((prev) => !prev)}
            className="rounded-xl bg-accent py-2 px-4 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
          >
            {showCreateForm ? "Cancel" : "Create organization"}
          </button>
        )}
      </div>

      {showCreateForm && (
        <div className="mt-4 rounded-xl border border-white/20 bg-white/10 p-4 backdrop-blur-sm">
          <input
            type="text"
            value={createName}
            onChange={(e) => setCreateName(e.target.value)}
            className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white placeholder-white/50"
            placeholder="Organization name"
          />
          <select
            value={createPlan}
            onChange={(e) => setCreatePlan(e.target.value as PlanType)}
            className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white"
          >
            {PLANS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          {createError && (
            <p className="mb-3 rounded-lg bg-red-500/20 p-2 text-sm text-red-100">
              {createError}
            </p>
          )}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleCreate}
              disabled={creating || createName.trim() === ""}
              className="rounded-xl bg-accent py-2 px-4 font-medium text-white transition-colors hover:bg-accent-hover disabled:opacity-50"
            >
              {creating ? "Creating..." : "Create"}
            </button>
            <button
              type="button"
              onClick={handleCancelCreate}
              disabled={creating}
              className="rounded-xl border-2 border-white/50 bg-white/10 py-2 px-4 font-medium text-white transition-colors hover:bg-white/20"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <p className="mt-4 text-white/80">Loading organizations...</p>
      ) : error ? (
        <p className="mt-4 rounded-lg bg-red-500/20 p-3 text-sm text-red-100">
          {error.message}
        </p>
      ) : organizations.length === 0 && !showCreateForm ? (
        <p className="mt-4 text-white/80">No organizations yet.</p>
      ) : (
        <div className="mt-4 flex flex-col gap-3">
          {organizations.map((org) => (
            <OrganizationCard
              key={org.id}
              org={org}
              onUpdate={handleOrgUpdate}
              onDelete={handleOrgDelete}
              getToken={getToken}
            />
          ))}
        </div>
      )}
    </div>
  );
}
