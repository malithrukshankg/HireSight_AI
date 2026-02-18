import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, Outlet } from "react-router-dom";

/**
 * Wraps routes that require authentication.
 * Redirects to /login when not authenticated.
 */
export function ProtectedRoute() {
  const { isLoading, isAuthenticated } = useAuth0();

  if (isLoading) return "Loading...";

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
