import { useAuth0 } from "@auth0/auth0-react";
import { Link } from "react-router-dom";

export function Header() {
  const { isAuthenticated, logout, user } = useAuth0();

  return (
    <header className="shrink-0 border-b border-neutral-200 bg-white">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2">
          <div className="grid h-8 w-8 grid-cols-2 grid-rows-2 gap-0.5">
            <div className="rounded-sm bg-violet-600" />
            <div className="rounded-sm bg-violet-600" />
            <div className="rounded-sm bg-violet-600" />
            <div className="rounded-sm bg-violet-600" />
          </div>
          <span className="text-lg font-semibold text-neutral-900">HireSight</span>
        </Link>
        <nav className="flex items-center gap-6">
          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              <span className="text-sm text-neutral-600">{user?.email}</span>
              <button
                type="button"
                onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
                className="text-sm font-medium text-neutral-600 hover:text-neutral-900"
              >
                Logout
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="text-sm font-medium text-neutral-600 hover:text-neutral-900"
            >
              Sign in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
