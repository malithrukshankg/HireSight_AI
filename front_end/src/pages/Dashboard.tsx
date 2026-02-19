import { useAuth0 } from "@auth0/auth0-react";
import { useEnsureUser } from "../hooks/useEnsureUser";

export default function Dashboard() {
  const { user, getAccessTokenSilently, logout: auth0Logout } = useAuth0();
  const { error: upsertError } = useEnsureUser();

  const printAccessToken = async () => {
    const token = await getAccessTokenSilently();
    console.log("ACCESS TOKEN:", token);
  };

  return (
    <>
      {upsertError && <p>Could not sync user: {upsertError.message}</p>}
      <p>Logged in as {user?.email}</p>

      <button onClick={printAccessToken}>Print Access Token</button>

      <pre>{JSON.stringify(user, null, 2)}</pre>

      <button onClick={() => auth0Logout({ logoutParams: { returnTo: window.location.origin } })}>
        Logout
      </button>
    </>
  );
}
