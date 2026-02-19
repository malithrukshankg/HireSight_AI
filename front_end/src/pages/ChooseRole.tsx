import { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from "react-router-dom";
import { useEnsureUser } from "../hooks/useEnsureUser";
import { useCurrentRole } from "../hooks/useCurrentRole";
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
      const token = await getAccessTokenSilently();
      await switchRole(token, newRole);
      await getAccessTokenSilently({ ignoreCache: true });
      window.location.reload();
    } catch (e) {
      setRoleSwitchError(e instanceof Error ? e.message : String(e));
    } finally {
      setRoleSwitchLoading(false);
    }
  };

  return (
    <main className="flex min-h-0 flex-1 flex-col items-center justify-center overflow-auto p-8">
      <div className="mx-auto w-full max-w-md space-y-6">
        {upsertError && (
          <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
            Could not sync user: {upsertError.message}
          </p>
        )}

        <h1 className="text-2xl font-bold text-neutral-900">Choose your role</h1>

        <p className="text-neutral-600">
          You are logged in as <strong className="text-neutral-900">{currentRole}</strong>. If you
          like to continue in this role click Continue.
        </p>

        <div className="flex flex-col gap-3">
          <button
            type="button"
            onClick={handleContinue}
            disabled={roleSwitchLoading}
            className="w-full rounded-xl bg-neutral-900 py-3 px-5 font-medium text-white transition-colors hover:bg-neutral-800 focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 disabled:opacity-50"
          >
            Continue
          </button>

          {otherRole && (
            <>
              <p className="text-neutral-600">
                If not change role to <strong className="text-neutral-900">{otherRole}</strong>.
              </p>
              <button
                type="button"
                onClick={() => handleSwitchRole(otherRole)}
                disabled={roleSwitchLoading}
                className="w-full rounded-xl border-2 border-neutral-900 py-3 px-5 font-medium text-neutral-900 transition-colors hover:bg-neutral-100 focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 disabled:opacity-50"
              >
                Change role to {otherRole}
              </button>
            </>
          )}
        </div>

        {roleSwitchError && (
          <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">{roleSwitchError}</p>
        )}
      </div>
    </main>
  );
}
