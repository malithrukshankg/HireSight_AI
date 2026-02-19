import { useAuth0 } from "@auth0/auth0-react";
import { Link } from "react-router-dom";
import { useCurrentRole } from "../../hooks/useCurrentRole";

export function Header() {
  const { isAuthenticated, logout, user } = useAuth0();
  const role = useCurrentRole();

  const homePath = isAuthenticated && ["admin", "recruiter", "candidate"].includes(role)
    ? `/${role}`
    : "/";

  return (
    <header className="shrink-0 border-b border-white/10 bg-black/20 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to={homePath} className="flex items-center gap-2">
          <div className="grid h-8 w-8 grid-cols-2 grid-rows-2 gap-0.5">
            <div className="rounded-sm bg-accent" />
            <div className="rounded-sm bg-accent" />
            <div className="rounded-sm bg-accent" />
            <div className="rounded-sm bg-accent" />
          </div>
          <span className="text-lg font-semibold text-white">HireSight</span>
        </Link>
        <nav className="flex items-center gap-6">
          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              <span className="text-sm text-white/90">{user?.email}</span>
              <button
                type="button"
                onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
                className="text-sm font-medium text-white/90 transition-colors hover:text-accent"
              >
                Logout
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="text-sm font-medium text-white/90 transition-colors hover:text-accent"
            >
              Sign in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
