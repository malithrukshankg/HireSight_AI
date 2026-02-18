import { useAuth0 } from "@auth0/auth0-react";
import { Navigate } from "react-router-dom";

export default function Login() {
  const { isAuthenticated, error, loginWithRedirect: login } = useAuth0();

  const signup = () =>
    login({ authorizationParams: { screen_hint: "signup" } });

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <>
      {error && <p>Error: {error.message}</p>}

      <button onClick={signup}>Signup</button>

      <button onClick={() => login()}>Login</button>
    </>
  );
}
