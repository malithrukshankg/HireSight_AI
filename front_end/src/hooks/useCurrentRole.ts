import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

/**
 * Extracts role from the access token JWT (same claims the backend reads).
 * Auth0 user object comes from ID token and may not include role; the access token has it.
 */
function getRoleFromAccessToken(token: string): string {
  try {
    const [, payloadB64] = token.split(".");
    if (!payloadB64) return "candidate";
    const payloadJson = atob(payloadB64.replace(/-/g, "+").replace(/_/g, "/"));
    const payload = JSON.parse(payloadJson) as Record<string, unknown>;
    // Backend reads: role, https://hiresight.ai/role, or authorization.roles
    let role: unknown = payload.role ?? payload["https://hiresight.ai/role"];
    if (role == null) {
      const roles = (payload.authorization as { roles?: unknown[] })?.roles;
      const first = Array.isArray(roles) ? roles[0] : undefined;
      role = typeof first === "string" ? first : (first as { name?: string })?.name;
    }
    const roleStr = typeof role === "string" ? role.toLowerCase() : "";
    if (["admin", "recruiter", "candidate"].includes(roleStr)) {
      return roleStr;
    }
  } catch {
    // ignore decode errors
  }
  return "candidate";
}

/**
 * Returns the current user's role from the access token.
 * Used for role switch UI so we correctly enable/disable the Candidate vs Recruiter buttons.
 */
export function useCurrentRole(): string {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();
  const [currentRole, setCurrentRole] = useState<string>("candidate");

  useEffect(() => {
    if (!isAuthenticated) {
      setCurrentRole("candidate");
      return;
    }
    let cancelled = false;
    getAccessTokenSilently()
      .then((token) => {
        if (!cancelled) setCurrentRole(getRoleFromAccessToken(token));
      })
      .catch(() => {
        if (!cancelled) setCurrentRole("candidate");
      });
    return () => {
      cancelled = true;
    };
  }, [getAccessTokenSilently, isAuthenticated]);

  return currentRole;
}
