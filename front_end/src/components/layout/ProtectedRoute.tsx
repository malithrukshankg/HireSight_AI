import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

/**
 * Wraps routes that require authentication.
 * Redirects to /login when not authenticated, preserving the attempted path for return after login.
 */
export function ProtectedRoute() {
  const { isLoading, isAuthenticated } = useAuth0();
  const location = useLocation();

  if (isLoading) return "Loading...";

  if (!isAuthenticated) {
    const returnTo = encodeURIComponent(location.pathname);
    return <Navigate to={`/login?returnTo=${returnTo}`} replace />;
  }

  return <Outlet />;
}
