"""
Auth0 Management API client for server-side operations.
Used for role assignment (switch role) via M2M credentials.
"""
import os
import httpx

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_M2M_CLIENT_ID = os.getenv("AUTH0_M2M_CLIENT_ID")
AUTH0_M2M_CLIENT_SECRET = os.getenv("AUTH0_M2M_CLIENT_SECRET")
AUTH0_ROLE_ID_CANDIDATE = os.getenv("AUTH0_ROLE_ID_CANDIDATE")
AUTH0_ROLE_ID_RECRUITER = os.getenv("AUTH0_ROLE_ID_RECRUITER")

# Only candidate and recruiter are self-assignable; admin is NOT.
SELF_ASSIGNABLE_ROLES = ("candidate", "recruiter")
ROLE_ID_MAP = {
    "candidate": AUTH0_ROLE_ID_CANDIDATE,
    "recruiter": AUTH0_ROLE_ID_RECRUITER,
}


def _validate_config() -> None:
    """Raise if required env vars are missing."""
    if not AUTH0_DOMAIN or not AUTH0_M2M_CLIENT_ID or not AUTH0_M2M_CLIENT_SECRET:
        raise RuntimeError(
            "Missing Auth0 M2M config. Set AUTH0_DOMAIN, AUTH0_M2M_CLIENT_ID, AUTH0_M2M_CLIENT_SECRET."
        )
    if not AUTH0_ROLE_ID_CANDIDATE or not AUTH0_ROLE_ID_RECRUITER:
        raise RuntimeError(
            "Missing Auth0 role IDs. Set AUTH0_ROLE_ID_CANDIDATE and AUTH0_ROLE_ID_RECRUITER."
        )


def get_role_id(role: str) -> str:
    """
    Map role name to Auth0 role ID.
    Only 'candidate' and 'recruiter' are allowed (admin is NOT self-assignable).
    """
    _validate_config()
    if role not in SELF_ASSIGNABLE_ROLES:
        raise ValueError(
            f"Invalid role: {role}. Only 'candidate' and 'recruiter' are self-assignable."
        )
    role_id = ROLE_ID_MAP.get(role)
    if not role_id:
        raise RuntimeError(
            f"Role ID not configured for '{role}'. Set AUTH0_ROLE_ID_{role.upper()}."
        )
    return role_id


async def get_management_token() -> str:
    """Obtain Management API access token via client_credentials."""
    _validate_config()
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            headers={"Content-Type": "application/json"},
            json={
                "client_id": AUTH0_M2M_CLIENT_ID,
                "client_secret": AUTH0_M2M_CLIENT_SECRET,
                "audience": f"https://{AUTH0_DOMAIN}/api/v2/",
                "grant_type": "client_credentials",
            },
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Auth0 token request failed: {resp.status_code} {resp.text}"
            )
        data = resp.json()
        token = data.get("access_token")
        if not token:
            raise RuntimeError("Auth0 token response missing access_token")
        return token


async def assign_role_to_user(user_id: str, role: str) -> None:
    """
    Assign the given role to the user and remove the other self-assignable role.
    Role must be 'candidate' or 'recruiter'. Admin is never assignable.
    """
    role_id = get_role_id(role)
    other_role = "recruiter" if role == "candidate" else "candidate"
    other_role_id = ROLE_ID_MAP.get(other_role)

    token = await get_management_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    base_url = f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}"

    async with httpx.AsyncClient(timeout=15) as client:
        # 1) Remove the other role so user has exactly one
        if other_role_id:
            del_resp = await client.request(
                "DELETE",
                f"{base_url}/roles",
                headers=headers,
                json={"roles": [other_role_id]},
            )
            if del_resp.status_code not in (200, 204):
                raise RuntimeError(
                    f"Auth0 remove role failed: {del_resp.status_code} {del_resp.text}"
                )

        # 2) Assign the new role
        post_resp = await client.post(
            f"{base_url}/roles",
            headers=headers,
            json={"roles": [role_id]},
        )
        if post_resp.status_code not in (200, 204):
            raise RuntimeError(
                f"Auth0 assign role failed: {post_resp.status_code} {post_resp.text}"
            )
