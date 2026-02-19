import { Navigate, Outlet } from "react-router-dom";
import { useCurrentRole } from "../../hooks/useCurrentRole";

type RoleGuardProps = {
  allowedRoles: string[];
};

/**
 * Protects role-specific routes. Redirects to the correct role home
 * when the user's role doesn't match the route.
 */
export function RoleGuard({ allowedRoles }: RoleGuardProps) {
  const currentRole = useCurrentRole();

  if (!allowedRoles.includes(currentRole)) {
    const homePath = ["admin", "recruiter", "candidate"].includes(currentRole)
      ? `/${currentRole}`
      : "/role";
    return <Navigate to={homePath} replace />;
  }

  return <Outlet />;
}
