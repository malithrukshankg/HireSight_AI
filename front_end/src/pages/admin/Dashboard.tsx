import { useAuth0 } from "@auth0/auth0-react";
import { useEnsureUser } from "../../hooks/useEnsureUser";

export default function AdminDashboard() {
  const { user, getAccessTokenSilently, logout: auth0Logout } = useAuth0();
  const { error: upsertError } = useEnsureUser();

  const printAccessToken = async () => {
    const token = await getAccessTokenSilently();
    console.log("ACCESS TOKEN:", token);
  };

  return (
    <main className="flex min-h-0 flex-1 flex-col overflow-auto p-8 lg:p-16">
      <div className="mx-auto w-full max-w-2xl">
        {upsertError && (
          <p className="mb-4 rounded-lg bg-red-500/20 p-3 text-sm text-red-100">
            Could not sync user: {upsertError.message}
          </p>
        )}
        <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
        <p className="mt-2 text-white/90">Logged in as {user?.email}</p>

        <div className="mt-8 rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
          <h2 className="text-lg font-semibold text-white">Debug</h2>
          <button
            type="button"
            onClick={printAccessToken}
            className="mt-4 rounded-xl bg-accent py-2 px-4 font-medium text-white transition-colors hover:bg-accent-hover"
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
      </div>
    </main>
  );
}
