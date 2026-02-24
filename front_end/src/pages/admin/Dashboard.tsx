import { useAuth0 } from "@auth0/auth0-react";
import { StatCard } from "../../components/ui/StatCard";
import { useEnsureUser } from "../../hooks/useEnsureUser";

function UsersIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  );
}

export default function AdminDashboard() {
  const { user, getAccessTokenSilently, logout: auth0Logout } = useAuth0();
  const { error: upsertError } = useEnsureUser();

  const printAccessToken = async () => {
    const token = await getAccessTokenSilently();
    console.log("ACCESS TOKEN:", token);
  };

  return (
    <main className="flex min-h-0 flex-1 flex-col p-6 lg:p-8">
      <div className="w-full">
        {upsertError && (
          <p className="mb-4 rounded-lg bg-red-500/20 p-3 text-sm text-red-100">
            Could not sync user: {upsertError.message}
          </p>
        )}

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
          <p className="mt-1 text-white/90">Welcome back, {user?.email}</p>
        </div>

        {/* Stat cards - admin metrics placeholders */}
        <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-3">
          <StatCard
            title="Admin Access"
            value="Active"
            icon={<ShieldIcon />}
            iconBgClass="bg-accent/80"
          />
          <StatCard
            title="System Status"
            value="Online"
            icon={<SettingsIcon />}
            iconBgClass="bg-green-500/80"
          />
          <StatCard
            title="Role"
            value="Admin"
            icon={<UsersIcon />}
            iconBgClass="bg-blue-500/80"
          />
        </div>

        {/* Main content area - full width */}
        <div className="mb-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
            <h2 className="mb-4 text-lg font-semibold text-white">Quick actions</h2>
            <p className="text-sm text-white/80">
              Admin tools and system management will be available here.
            </p>
          </div>

          <div className="rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
            <h2 className="mb-4 text-lg font-semibold text-white">Overview</h2>
            <p className="text-sm text-white/80">
              Use the atmospheric warm theme consistently across the dashboard.
            </p>
          </div>
        </div>

        {/* Debug - collapsible */}
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
