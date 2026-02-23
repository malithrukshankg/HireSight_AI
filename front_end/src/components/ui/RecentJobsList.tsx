import type { Job } from "../../types/job";

type RecentJobsListProps = {
  jobs: Job[];
  getOrgName: (orgId: string) => string;
  maxItems?: number;
};

const statusColors: Record<string, string> = {
  open: "bg-green-500/30 text-green-100",
  draft: "bg-amber-500/30 text-amber-100",
  closed: "bg-slate-500/30 text-slate-200",
};

export function RecentJobsList({
  jobs,
  getOrgName,
  maxItems = 5,
}: RecentJobsListProps) {
  const displayJobs = jobs.slice(0, maxItems);

  return (
    <div className="flex flex-col gap-2">
      {displayJobs.length === 0 ? (
        <p className="py-4 text-center text-sm text-white/70">No jobs yet</p>
      ) : (
        displayJobs.map((job) => (
          <div
            key={job.id}
            className="flex items-center justify-between rounded-lg border border-white/10 bg-white/5 px-3 py-2 transition-colors hover:bg-white/10"
          >
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium text-white">{job.title}</p>
              <p className="truncate text-xs text-white/70">{getOrgName(job.organization_id)}</p>
            </div>
            <span
              className={`ml-2 shrink-0 rounded-md px-2 py-0.5 text-xs font-medium ${statusColors[job.status] ?? "bg-white/20 text-white"}`}
            >
              {job.status}
            </span>
          </div>
        ))
      )}
    </div>
  );
}
