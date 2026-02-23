import { useCallback, useEffect, useState } from "react";
import { getMyJobs, createJob } from "../../services/jobService";
import { getOrganizationsForCurrentUser } from "../../services/organizationService";
import type { Job, JobCreate, JobStatus } from "../../types/job";
import type { Organization } from "../../types/organization";

const EMPLOYMENT_TYPES = [
  "Full-time",
  "Part-time",
  "Contract",
  "Internship",
  "Freelance",
];

const JOB_STATUSES: JobStatus[] = ["draft", "open", "closed"];

function JobCard({
  job,
  orgName,
}: {
  job: Job;
  orgName: string;
}) {
  return (
    <div className="flex flex-col gap-1 rounded-xl border border-white/20 bg-white/10 p-4 backdrop-blur-sm">
      <p className="font-medium text-white">{job.title}</p>
      <p className="text-sm text-white/80">{orgName}</p>
      <p className="text-sm text-white/70">
        {job.location} · {job.employment_type}
      </p>
      <span className="mt-1 inline-flex w-fit rounded-lg bg-white/20 px-2 py-0.5 text-xs font-medium text-white">
        {job.status}
      </span>
    </div>
  );
}

export type JobsTileProps = {
  getToken: () => Promise<string>;
};

export function JobsTile({ getToken }: JobsTileProps) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [filterOrgId, setFilterOrgId] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createOrgId, setCreateOrgId] = useState("");
  const [createTitle, setCreateTitle] = useState("");
  const [createDescription, setCreateDescription] = useState("");
  const [createLocation, setCreateLocation] = useState("");
  const [createEmploymentType, setCreateEmploymentType] = useState(
    EMPLOYMENT_TYPES[0]
  );
  const [createStatus, setCreateStatus] = useState<JobStatus>("draft");

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const token = await getToken();
      const [jobsData, orgsData] = await Promise.all([
        getMyJobs(token),
        getOrganizationsForCurrentUser(token),
      ]);
      setJobs(jobsData);
      setOrganizations(orgsData);
      setCreateOrgId((prev) => prev || (orgsData[0]?.id ?? ""));
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)));
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const filteredJobs =
    filterOrgId == null
      ? jobs
      : jobs.filter((j) => j.organization_id === filterOrgId);

  const getOrgName = (orgId: string) => {
    const org = organizations.find((o) => o.id === orgId);
    return org?.name ?? "Unknown";
  };

  const handleCreate = async () => {
    if (
      !createOrgId ||
      createTitle.trim() === "" ||
      createDescription.trim() === "" ||
      createLocation.trim() === ""
    ) {
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const token = await getToken();
      const payload: JobCreate = {
        organization_id: createOrgId,
        title: createTitle.trim(),
        description: createDescription.trim(),
        location: createLocation.trim(),
        employment_type: createEmploymentType,
        status: createStatus,
      };
      const created = await createJob(token, payload);
      setJobs((prev) => [created, ...prev]);
      setCreateOrgId(organizations[0]?.id ?? "");
      setCreateTitle("");
      setCreateDescription("");
      setCreateLocation("");
      setCreateEmploymentType(EMPLOYMENT_TYPES[0]);
      setCreateStatus("draft");
      setShowCreateForm(false);
    } catch (e) {
      setCreateError(e instanceof Error ? e.message : String(e));
    } finally {
      setCreating(false);
    }
  };

  const handleCancelCreate = () => {
    setShowCreateForm(false);
    setCreateTitle("");
    setCreateDescription("");
    setCreateLocation("");
    setCreateEmploymentType(EMPLOYMENT_TYPES[0]);
    setCreateStatus("draft");
    setCreateError(null);
  };

  const canCreate = organizations.length > 0;
  const isFormValid =
    createOrgId &&
    createTitle.trim() !== "" &&
    createDescription.trim() !== "" &&
    createLocation.trim() !== "";

  return (
    <div className="rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Jobs</h2>
        {!loading && !error && canCreate && (
          <button
            type="button"
            onClick={() => setShowCreateForm((prev) => !prev)}
            className="rounded-xl bg-accent py-2 px-4 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
          >
            {showCreateForm ? "Cancel" : "Create job"}
          </button>
        )}
      </div>

      {!loading && !error && (
        <div className="mt-4 flex items-center gap-2">
          <label htmlFor="filter-org" className="text-sm text-white/80">
            Filter by organization:
          </label>
          <select
            id="filter-org"
            value={filterOrgId ?? ""}
            onChange={(e) =>
              setFilterOrgId(e.target.value === "" ? null : e.target.value)
            }
            className="rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-sm text-white"
          >
            <option value="">All</option>
            {organizations.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {showCreateForm && (
        <div className="mt-4 rounded-xl border border-white/20 bg-white/10 p-4 backdrop-blur-sm">
          <select
            value={createOrgId}
            onChange={(e) => setCreateOrgId(e.target.value)}
            className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white"
          >
            <option value="">Select organization</option>
            {organizations.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </select>
          <input
            type="text"
            value={createTitle}
            onChange={(e) => setCreateTitle(e.target.value)}
            className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white placeholder-white/50"
            placeholder="Job title"
          />
          <textarea
            value={createDescription}
            onChange={(e) => setCreateDescription(e.target.value)}
            rows={3}
            className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white placeholder-white/50"
            placeholder="Job description"
          />
          <input
            type="text"
            value={createLocation}
            onChange={(e) => setCreateLocation(e.target.value)}
            className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white placeholder-white/50"
            placeholder="Location"
          />
          <select
            value={createEmploymentType}
            onChange={(e) => setCreateEmploymentType(e.target.value)}
            className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white"
          >
            {EMPLOYMENT_TYPES.map((et) => (
              <option key={et} value={et}>
                {et}
              </option>
            ))}
          </select>
          <select
            value={createStatus}
            onChange={(e) => setCreateStatus(e.target.value as JobStatus)}
            className="mb-3 w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-white"
          >
            {JOB_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
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
              disabled={creating || !isFormValid}
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
        <p className="mt-4 text-white/80">Loading jobs...</p>
      ) : error ? (
        <p className="mt-4 rounded-lg bg-red-500/20 p-3 text-sm text-red-100">
          {error.message}
        </p>
      ) : !canCreate && !showCreateForm ? (
        <p className="mt-4 text-white/80">
          Create an organization first to add jobs.
        </p>
      ) : filteredJobs.length === 0 && !showCreateForm ? (
        <p className="mt-4 text-white/80">
          {filterOrgId ? "No jobs in this organization." : "No jobs yet."}
        </p>
      ) : (
        <div className="mt-4 flex flex-col gap-3">
          {filteredJobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              orgName={getOrgName(job.organization_id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
