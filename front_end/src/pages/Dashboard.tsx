import { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { useEnsureUser } from "../hooks/useEnsureUser";
import { switchRole } from "../services/userService";

export default function Dashboard() {
  const { user, getAccessTokenSilently, logout: auth0Logout } = useAuth0();
  const { error: upsertError } = useEnsureUser();
  const [roleSwitchLoading, setRoleSwitchLoading] = useState(false);
  const [roleSwitchError, setRoleSwitchError] = useState<string | null>(null);

  const handleSwitchRole = async (newRole: "candidate" | "recruiter") => {
    if (roleSwitchLoading) return;
    setRoleSwitchError(null);
    setRoleSwitchLoading(true);
    try {
      const token = await getAccessTokenSilently();
      await switchRole(token, newRole);
      // Token refresh: getAccessTokenSilently({ ignoreCache: true }) fetches a new token
      // so the JWT contains the updated role. Reload to re-run useEnsureUser and sync DB.
      await getAccessTokenSilently({ ignoreCache: true });
      window.location.reload();
    } catch (e) {
      setRoleSwitchError(e instanceof Error ? e.message : String(e));
    } finally {
      setRoleSwitchLoading(false);
    }
  };

  const printAccessToken = async () => {
    const token = await getAccessTokenSilently();
    console.log("ACCESS TOKEN:", token);
  };

  return (
    <>
      {upsertError && <p>Could not sync user: {upsertError.message}</p>}
      <p>Logged in as {user?.email}</p>

      <div>
        <span>Role: </span>
        <button
          onClick={() => handleSwitchRole("candidate")}
          disabled={roleSwitchLoading}
        >
          Candidate
        </button>
        <button
          onClick={() => handleSwitchRole("recruiter")}
          disabled={roleSwitchLoading}
        >
          Recruiter
        </button>
        {roleSwitchError && <p style={{ color: "red" }}>{roleSwitchError}</p>}
      </div>

      <button onClick={printAccessToken}>Print Access Token</button>

      <pre>{JSON.stringify(user, null, 2)}</pre>

      <button onClick={() => auth0Logout({ logoutParams: { returnTo: window.location.origin } })}>
        Logout
      </button>
    </>
  );
}
