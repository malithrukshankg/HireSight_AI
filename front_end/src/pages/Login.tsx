import { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";

export default function Login() {
  const { isAuthenticated, error, loginWithPopup } = useAuth0();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const returnTo = searchParams.get("returnTo") || "/";
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
    <main className="grid min-h-0 flex-1 grid-cols-1 overflow-hidden lg:grid-cols-2">
      {/* Left panel - Login form */}
      <section className="flex min-h-0 flex-col justify-center overflow-hidden bg-white p-8 lg:p-16">
        <div className="mx-auto w-full max-w-md">
          {/* Branding */}
          <div className="mb-10 flex items-center gap-2">
            <div className="grid h-9 w-9 grid-cols-2 grid-rows-2 gap-0.5">
              <div className="rounded-sm bg-violet-600" />
              <div className="rounded-sm bg-violet-600" />
              <div className="rounded-sm bg-violet-600" />
              <div className="rounded-sm bg-violet-600" />
            </div>
            <span className="text-xl font-semibold text-neutral-900">HireSight</span>
          </div>

          <h1 className="text-3xl font-bold text-neutral-900">Welcome back</h1>
          <p className="mt-2 text-neutral-500">Please sign in to continue</p>
          <p className="mt-4 text-sm text-neutral-400">
            A sign-in window will open. Close it anytime to cancel.
          </p>

          {error && (
            <p className="mt-6 rounded-lg bg-red-50 p-3 text-sm text-red-600">
              {error.message}
            </p>
          )}

          <div className="mt-8 flex flex-col gap-4">
            <button
              type="button"
              onClick={doLogin}
              disabled={isLoading}
              className="w-full rounded-xl bg-neutral-900 py-3 px-5 font-medium text-white transition-colors hover:bg-neutral-800 focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {isLoading ? "Opening..." : "Sign in"}
            </button>
            <button
              type="button"
              onClick={doLoginWithGoogle}
              disabled={isLoading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-neutral-900 py-3 px-5 font-medium text-white transition-colors hover:bg-neutral-800 focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 disabled:opacity-50"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" aria-hidden>
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              {isLoading ? "Opening..." : "Sign in with Google"}
            </button>
          </div>

          <p className="mt-8 flex flex-wrap items-center justify-center gap-2 text-sm text-neutral-600">
            Don&apos;t have an account?{" "}
            <button
              type="button"
              onClick={signup}
              disabled={isLoading}
              className="rounded-xl bg-neutral-900 px-4 py-2 font-medium text-violet-400 transition-colors hover:bg-neutral-800 hover:text-violet-300 focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50"
            >
              Sign up
            </button>
          </p>
        </div>
      </section>

      {/* Right panel - Illustration */}
      <section className="hidden min-h-0 flex-col items-center justify-center overflow-hidden bg-[#E8E0F5] p-8 lg:flex">
        <div className="relative flex h-full w-full max-w-lg items-center justify-center">
          {/* Decorative background icons */}
          <div className="absolute inset-0 overflow-hidden">
            <svg
              className="absolute right-1/4 top-1/4 h-12 w-12 text-white/40"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <svg
              className="absolute bottom-1/3 left-1/4 h-10 w-10 text-white/40"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            <svg
              className="absolute right-1/3 top-1/3 h-8 w-8 text-white/30"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <svg
              className="absolute bottom-1/4 right-1/4 h-10 w-10 text-white/30"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <div className="absolute left-1/3 top-1/2 h-16 w-16 rounded-full border-2 border-white/30" />
            <div className="absolute bottom-1/3 right-1/3 h-3 w-3 rounded-full bg-white/40" />
          </div>
          {/* Main illustration placeholder - checkmark in circle */}
          <div className="relative flex h-48 w-48 items-center justify-center rounded-full border-2 border-white/50 bg-white/20">
            <svg className="h-24 w-24 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
      </section>
    </main>
  );
}
