import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, useSearchParams } from "react-router-dom";

export default function Login() {
  const { isAuthenticated, error, loginWithRedirect: login } = useAuth0();
  const [searchParams] = useSearchParams();
  const returnTo = searchParams.get("returnTo") || "/";

  const signup = () =>
    login({ appState: { returnTo }, authorizationParams: { screen_hint: "signup" } });

  const doLogin = () => login({ appState: { returnTo } });

  if (isAuthenticated) {
    return <Navigate to={returnTo} replace />;
  }

  return (
    <>
      {error && <p>Error: {error.message}</p>}

      <button onClick={signup}>Signup</button>

      <button onClick={doLogin}>Login</button>
    </>
  );
}
