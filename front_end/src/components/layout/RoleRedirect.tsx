import { Navigate } from "react-router-dom";
import { useCurrentRole } from "../../hooks/useCurrentRole";

/**
 * Redirects / to the user's role-specific home path.
 */
export function RoleRedirect() {
  const role = useCurrentRole();

  if (["admin", "recruiter", "candidate"].includes(role)) {
    return <Navigate to={`/${role}`} replace />;
  }

  return <Navigate to="/role" replace />;
}
