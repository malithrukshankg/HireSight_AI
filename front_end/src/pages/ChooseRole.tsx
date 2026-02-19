import { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from "react-router-dom";
import { useEnsureUser } from "../hooks/useEnsureUser";
import { useCurrentRole, getRoleFromAccessToken } from "../hooks/useCurrentRole";
import { switchRole } from "../services/userService";

export default function ChooseRole() {
  const { getAccessTokenSilently } = useAuth0();
  const navigate = useNavigate();
  const { error: upsertError } = useEnsureUser();
  const currentRole = useCurrentRole();
  const [roleSwitchLoading, setRoleSwitchLoading] = useState(false);
  const [roleSwitchError, setRoleSwitchError] = useState<string | null>(null);

  const otherRole =
    currentRole === "candidate"
      ? "recruiter"
      : currentRole === "recruiter"
        ? "candidate"
        : null;

  const handleContinue = () => {
    navigate("/", { replace: true });
  };

  const handleSwitchRole = async (newRole: "candidate" | "recruiter") => {
    if (roleSwitchLoading) return;
    setRoleSwitchError(null);
    setRoleSwitchLoading(true);
    try {
      const tokenBefore = await getAccessTokenSilently();
      // #region agent log
      fetch('http://127.0.0.1:7783/ingest/622dd89e-3f12-40a9-8ec7-11b4ee504506',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'998b02'},body:JSON.stringify({sessionId:'998b02',location:'ChooseRole.tsx:beforeSwitch',message:'Token role before switch',data:{newRole,roleBefore:getRoleFromAccessToken(tokenBefore)},timestamp:Date.now(),hypothesisId:'H2'})}).catch(()=>{});
      // #endregion
      await switchRole(tokenBefore, newRole);
      const tokenAfter = await getAccessTokenSilently({ cacheMode: "off" });
      // #region agent log
      fetch('http://127.0.0.1:7783/ingest/622dd89e-3f12-40a9-8ec7-11b4ee504506',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'998b02'},body:JSON.stringify({sessionId:'998b02',location:'ChooseRole.tsx:afterCacheBypass',message:'Token role after cacheMode:off',data:{roleAfter:getRoleFromAccessToken(tokenAfter)},timestamp:Date.now(),hypothesisId:'H1'})}).catch(()=>{});
      // #endregion
      window.location.reload();
    } catch (e) {
      setRoleSwitchError(e instanceof Error ? e.message : String(e));
    } finally {
      setRoleSwitchLoading(false);
    }
  };

  return (
    <main className="flex min-h-0 flex-1 flex-col items-center justify-center overflow-auto bg-white p-8 lg:p-16">
      <div className="mx-auto w-full max-w-2xl text-center">
        <h1 className="text-3xl font-bold text-neutral-900">Choose your role</h1>
        <p className="mt-2 text-neutral-500">Confirm how you&apos;d like to use HireSight</p>

        {upsertError && (
          <p className="mt-6 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            Could not sync user: {upsertError.message}
          </p>
        )}

        <div className="mt-8 rounded-xl border border-neutral-200 bg-neutral-50 p-5">
          <p className="text-neutral-700">
            You are logged in as{" "}
            <span className="inline-flex items-center rounded-full bg-violet-100 px-3 py-0.5 text-sm font-semibold text-violet-700">
              {currentRole}
            </span>
            . If you like to continue in this role click Continue.
          </p>
        </div>

        <div className="mt-6 flex flex-col gap-4">
          <button
            type="button"
            onClick={handleContinue}
            disabled={roleSwitchLoading}
            className="w-full rounded-xl bg-neutral-900 py-3 px-5 font-medium text-white transition-colors hover:bg-neutral-800 focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 disabled:opacity-50"
          >
            Continue as {currentRole}
          </button>

          {otherRole && (
            <div className="space-y-2">
              <p className="text-sm text-neutral-500">
                Or switch to <span className="font-medium text-neutral-700">{otherRole}</span>
              </p>
              <button
                type="button"
                onClick={() => handleSwitchRole(otherRole)}
                disabled={roleSwitchLoading}
                className="w-full rounded-xl border-2 border-violet-600 py-3 px-5 font-medium text-violet-600 transition-colors hover:bg-violet-50 focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {roleSwitchLoading ? "Switching..." : `Change role to ${otherRole}`}
              </button>
            </div>
          )}
        </div>

        {roleSwitchError && (
          <p className="mt-6 rounded-lg bg-red-50 p-3 text-sm text-red-600">{roleSwitchError}</p>
        )}
      </div>
    </main>
  );
}
