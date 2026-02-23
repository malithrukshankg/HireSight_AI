import { useAuth0 } from "@auth0/auth0-react";
import { useCallback, useEffect, useState } from "react";
import { JobsTile } from "../../components/ui/JobsTile";
import { JobStatusDonut, jobsToStatusData } from "../../components/ui/JobStatusDonut";
import { JobsBarChart, jobsToBarChartData } from "../../components/ui/JobsBarChart";
import { OrganizationsTile } from "../../components/ui/OrganizationsTile";
import { RecentJobsList } from "../../components/ui/RecentJobsList";
import { StatCard } from "../../components/ui/StatCard";
import { useEnsureUser } from "../../hooks/useEnsureUser";
import { getMyJobs } from "../../services/jobService";
import { getOrganizationsForCurrentUser } from "../../services/organizationService";
import type { Job } from "../../types/job";
import type { Organization } from "../../types/organization";

function OrganizationsIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    </svg>
  );
}

function JobsIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  );
}

function OpenIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  );
}

function DraftIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
    </svg>
  );
}

function ClosedIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

export default function RecruiterDashboard() {
  const { user, getAccessTokenSilently, logout: auth0Logout } = useAuth0();
  const { error: upsertError } = useEnsureUser();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState<Error | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setStatsError(null);
      const token = await getAccessTokenSilently();
      const [jobsData, orgsData] = await Promise.all([
        getMyJobs(token),
        getOrganizationsForCurrentUser(token),
      ]);
      setJobs(jobsData);
      setOrganizations(orgsData);
    } catch (e) {
      setStatsError(e instanceof Error ? e : new Error(String(e)));
    } finally {
      setStatsLoading(false);
    }
  }, [getAccessTokenSilently]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const getOrgName = (orgId: string) => {
    const org = organizations.find((o) => o.id === orgId);
    return org?.name ?? "Unknown";
  };

  const openCount = jobs.filter((j) => j.status === "open").length;
  const draftCount = jobs.filter((j) => j.status === "draft").length;
  const closedCount = jobs.filter((j) => j.status === "closed").length;
  const barData = jobsToBarChartData(jobs);
  const statusData = jobsToStatusData(jobs);
  const recentJobs = [...jobs].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const printAccessToken = async () => {
    const token = await getAccessTokenSilently();
    console.log("ACCESS TOKEN:", token);
  };

  return (
    <main className="flex min-h-0 flex-1 flex-col overflow-auto p-6 lg:p-10">
      <div className="mx-auto w-full max-w-7xl">
        {upsertError && (
          <p className="mb-4 rounded-lg bg-red-500/20 p-3 text-sm text-red-100">
            Could not sync user: {upsertError.message}
          </p>
        )}

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Recruiter Dashboard</h1>
          <p className="mt-1 text-white/90">Welcome back, {user?.email}</p>
        </div>

        {/* Stat cards row */}
        <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          <StatCard
            title="Organizations"
            value={statsLoading ? "—" : organizations.length}
            icon={<OrganizationsIcon />}
            iconBgClass="bg-blue-500/80"
          />
          <StatCard
            title="Total Jobs"
            value={statsLoading ? "—" : jobs.length}
            icon={<JobsIcon />}
            iconBgClass="bg-accent/80"
          />
          <StatCard
            title="Open"
            value={statsLoading ? "—" : openCount}
            icon={<OpenIcon />}
            iconBgClass="bg-green-500/80"
          />
          <StatCard
            title="Draft"
            value={statsLoading ? "—" : draftCount}
            icon={<DraftIcon />}
            iconBgClass="bg-amber-500/80"
          />
          <StatCard
            title="Closed"
            value={statsLoading ? "—" : closedCount}
            icon={<ClosedIcon />}
            iconBgClass="bg-slate-500/80"
          />
        </div>

        {/* Charts and recent jobs row */}
        <div className="mb-8 grid gap-6 lg:grid-cols-3">
          <div className="rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm lg:col-span-2">
            <h2 className="mb-4 text-lg font-semibold text-white">Jobs created</h2>
            {statsLoading ? (
              <div className="flex h-56 items-center justify-center text-white/70">Loading...</div>
            ) : statsError ? (
              <div className="flex h-56 items-center justify-center text-red-200">{statsError.message}</div>
            ) : (
              <JobsBarChart data={barData} />
            )}
          </div>

          <div className="rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
            <h2 className="mb-4 text-lg font-semibold text-white">Recent Jobs</h2>
            <RecentJobsList jobs={recentJobs} getOrgName={getOrgName} maxItems={6} />
          </div>
        </div>

        {/* Job status donut + organizations + jobs */}
        <div className="mb-8 grid gap-6 lg:grid-cols-3">
          <div className="rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
            <h2 className="mb-4 text-lg font-semibold text-white">Job Status</h2>
            {statsLoading ? (
              <div className="flex h-48 items-center justify-center text-white/70">Loading...</div>
            ) : (
              <JobStatusDonut data={statusData} />
            )}
          </div>

          <div className="lg:col-span-2">
            <OrganizationsTile getToken={getAccessTokenSilently} />
          </div>
        </div>

        {/* Jobs tile - full width */}
        <div className="mb-8">
          <JobsTile getToken={getAccessTokenSilently} />
        </div>

        {/* Debug - collapsible at bottom */}
        <details className="rounded-xl border border-white/20 bg-white/5 backdrop-blur-sm">
          <summary className="cursor-pointer px-6 py-4 text-sm font-medium text-white/80 hover:text-white">
            Debug
          </summary>
          <div className="border-t border-white/10 px-6 pb-6 pt-4">
            <button
              type="button"
              onClick={printAccessToken}
              className="rounded-xl bg-accent py-2 px-4 font-medium text-white transition-colors hover:bg-accent-hover"
            >
              Print Access Token
            </button>
            <pre className="mt-4 overflow-auto rounded-lg bg-black/30 p-4 text-sm text-white/90">
              {JSON.stringify(user, null, 2)}
            </pre>
            <button
              type="button"
              onClick={() => auth0Logout({ logoutParams: { returnTo: window.location.origin } })}
              className="mt-4 rounded-xl border-2 border-white/50 bg-white/10 py-2 px-4 font-medium text-white transition-colors hover:bg-white/20"
            >
              Logout
            </button>
          </div>
        </details>
      </div>
    </main>
  );
}
