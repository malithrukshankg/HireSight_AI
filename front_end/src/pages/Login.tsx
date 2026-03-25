import { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";

export default function Login() {
  const { isAuthenticated, error, loginWithPopup } = useAuth0();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const rawReturnTo = searchParams.get("returnTo");
  const decodedReturnTo = rawReturnTo ? decodeURIComponent(rawReturnTo) : null;
  const returnTo = !decodedReturnTo || decodedReturnTo === "/" ? "/role" : decodedReturnTo;
  const [isLoading, setIsLoading] = useState(false);

  const handleAuth = async (
    options: { appState?: { returnTo: string }; authorizationParams?: { screen_hint?: string; connection?: string } }
  ) => {
    setIsLoading(true);
    try {
      await loginWithPopup(options);
      navigate(returnTo, { replace: true });
    } catch (e) {
      // User closed popup or auth failed - stay on login page
    } finally {
      setIsLoading(false);
    }
  };

  const signup = () =>
    handleAuth({ appState: { returnTo }, authorizationParams: { screen_hint: "signup" } });

  const doLogin = () => handleAuth({ appState: { returnTo } });

  const doLoginWithGoogle = () =>
    handleAuth({ appState: { returnTo }, authorizationParams: { connection: "google-oauth2" } });

  if (isAuthenticated) {
    return <Navigate to={returnTo} replace />;
  }

  return (
    <main className="bg-atmospheric grid min-h-0 flex-1 grid-cols-1 overflow-hidden lg:grid-cols-2">
      {/* Left panel - Welcome message */}
      <section className="flex min-h-0 flex-col justify-center overflow-hidden p-8 lg:p-16">
        <div className="mx-auto w-full max-w-lg">
          <h1 className="text-4xl font-bold text-white lg:text-5xl">Welcome Back v2</h1>
          <p className="mt-4 text-lg leading-relaxed text-white/90">
            Connect with opportunities that match your skills. HireSight helps candidates find the right roles and recruiters discover top talent.
          </p>
          <div className="mt-12 flex gap-4">
            <a href="#" className="text-white/80 transition-colors hover:text-white" aria-label="Facebook">
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
            </a>
            <a href="#" className="text-white/80 transition-colors hover:text-white" aria-label="Twitter">
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            </a>
            <a href="#" className="text-white/80 transition-colors hover:text-white" aria-label="Instagram">
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            </a>
            <a href="#" className="text-white/80 transition-colors hover:text-white" aria-label="YouTube">
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            </a>
          </div>
        </div>
      </section>

      {/* Right panel - Sign in form */}
      <section className="flex min-h-0 flex-col justify-center overflow-hidden p-8 lg:p-16">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-10 flex items-center gap-2">
            <div className="grid h-9 w-9 grid-cols-2 grid-rows-2 gap-0.5">
              <div className="rounded-sm bg-accent" />
              <div className="rounded-sm bg-accent" />
              <div className="rounded-sm bg-accent" />
              <div className="rounded-sm bg-accent" />
            </div>
            <span className="text-xl font-semibold text-white">HireSight</span>
          </div>

          <h2 className="text-3xl font-bold text-white">Sign in</h2>
          <p className="mt-2 text-white/90">A sign-in window will open. Close it anytime to cancel.</p>

          {error && (
            <p className="mt-6 rounded-lg bg-red-500/20 p-3 text-sm text-red-100">
              {error.message}
            </p>
          )}

          <div className="mt-8 flex flex-col gap-4">
            <button
              type="button"
              onClick={doLogin}
              disabled={isLoading}
              className="w-full rounded-xl bg-accent py-3 px-5 font-medium text-white transition-colors hover:bg-accent-hover focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-0 disabled:opacity-50"
            >
              {isLoading ? "Opening..." : "Sign in now"}
            </button>
            <button
              type="button"
              onClick={doLoginWithGoogle}
              disabled={isLoading}
              className="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-white/30 bg-white/10 py-3 px-5 font-medium text-white transition-colors hover:bg-white/20 focus:ring-2 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-0 disabled:opacity-50"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" aria-hidden>
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              {isLoading ? "Opening..." : "Sign in with Google"}
            </button>
          </div>

          <p className="mt-8 flex flex-wrap items-center justify-center gap-2 text-sm text-white/90">
            Don&apos;t have an account?{" "}
            <button
              type="button"
              onClick={signup}
              disabled={isLoading}
              className="font-medium text-accent transition-colors hover:text-accent-light disabled:opacity-50"
            >
              Sign up
            </button>
          </p>

          <p className="mt-6 text-center text-xs text-white/70">
            By signing in you agree to our{" "}
            <a href="#" className="text-accent hover:underline">Terms of Service</a>
            {" "}|{" "}
            <a href="#" className="text-accent hover:underline">Privacy Policy</a>
          </p>
        </div>
      </section>
    </main>
  );
}
