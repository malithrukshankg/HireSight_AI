import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

/**
 * Extracts role from the access token JWT (same claims the backend reads).
 * Auth0 user object comes from ID token and may not include role; the access token has it.
 */
export function getRoleFromAccessToken(token: string): string {
  try {
    const [, payloadB64] = token.split(".");
    if (!payloadB64) return "candidate";
    const payloadJson = atob(payloadB64.replace(/-/g, "+").replace(/_/g, "/"));
    const payload = JSON.parse(payloadJson) as Record<string, unknown>;
    // Auth0 RBAC places roles in https://hiresight.local/roles (array). Also check legacy claims.
    const rolesArray = payload["https://hiresight.local/roles"];
    const firstFromArray = Array.isArray(rolesArray) ? rolesArray[0] : undefined;
    let role: unknown =
      (typeof firstFromArray === "string" ? firstFromArray : undefined) ??
      payload.role ??
      payload["https://hiresight.ai/role"];
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
        let payload: Record<string, unknown> = {};
        try {
          const [, payloadB64] = token.split(".");
          if (payloadB64) {
            const payloadJson = atob(payloadB64.replace(/-/g, "+").replace(/_/g, "/"));
            payload = JSON.parse(payloadJson) as Record<string, unknown>;
          }
        } catch {
          payload = {};
        }
        const role = getRoleFromAccessToken(token);
        // #region agent log
        const roleRelevant: Record<string, unknown> = {};
        for (const k of Object.keys(payload)) {
          if (k.includes("role") || k.includes("Role") || k.includes("authorization") || k.includes("permission") || k.startsWith("https://")) {
            roleRelevant[k] = payload[k];
          }
        }
        fetch('http://127.0.0.1:7783/ingest/622dd89e-3f12-40a9-8ec7-11b4ee504506',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'998b02'},body:JSON.stringify({sessionId:'998b02',location:'useCurrentRole.ts:effect',message:'Token payload for role debug',data:{extractedRole:role,roleRelatedClaims:roleRelevant,allClaimKeys:Object.keys(payload)},timestamp:Date.now(),hypothesisId:'H1'})}).catch(()=>{});
        // #endregion
        if (!cancelled) setCurrentRole(role);
      })
      .catch((err) => {
        // #region agent log
        fetch('http://127.0.0.1:7783/ingest/622dd89e-3f12-40a9-8ec7-11b4ee504506',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'998b02'},body:JSON.stringify({sessionId:'998b02',location:'useCurrentRole.ts:catch',message:'getAccessTokenSilently failed',data:{err:String(err)},timestamp:Date.now(),hypothesisId:'H4'})}).catch(()=>{});
        // #endregion
        if (!cancelled) setCurrentRole("candidate");
      });
    return () => {
      cancelled = true;
    };
  }, [getAccessTokenSilently, isAuthenticated]);

  return currentRole;
}
