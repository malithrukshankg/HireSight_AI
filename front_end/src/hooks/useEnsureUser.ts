import { useEffect, useRef, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { upsertUser } from "../services/userService";

/**
 * When the user is authenticated, calls the backend upsert endpoint once per session
 * so the user record exists or is updated. Call this in the app shell (e.g. App.tsx).
 */
export function useEnsureUser(): {
  isSyncing: boolean;
  error: Error | null;
} {
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();
  const hasUpsertedRef = useRef(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      hasUpsertedRef.current = false;
      return;
    }

    if (hasUpsertedRef.current) return;
    hasUpsertedRef.current = true;

    let cancelled = false;

    async function run() {
      setIsSyncing(true);
      setError(null);
      try {
        const token = await getAccessTokenSilently();
        if (cancelled) return;
        await upsertUser(token);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e : new Error(String(e)));
          hasUpsertedRef.current = false; // allow retry
        }
      } finally {
        if (!cancelled) setIsSyncing(false);
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, getAccessTokenSilently]);

  return { isSyncing, error };
}
