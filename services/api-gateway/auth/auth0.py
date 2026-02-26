import os
import time
import httpx
from jose import jwt
from jose.exceptions import JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
AUTH0_ISSUER = os.getenv("AUTH0_ISSUER")

if not AUTH0_DOMAIN or not AUTH0_AUDIENCE or not AUTH0_ISSUER:
    raise RuntimeError(
        "Missing AUTH0 env vars. Set AUTH0_DOMAIN, AUTH0_AUDIENCE, AUTH0_ISSUER."
    )

JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"

bearer_scheme = HTTPBearer(auto_error=True)

# Simple in-memory cache for JWKS (good enough for most apps)
_JWKS_CACHE: dict = {"keys": None, "fetched_at": 0}
JWKS_TTL_SECONDS = 60 * 60  # 1 hour


async def _get_jwks_keys() -> list[dict]:
    now = int(time.time())
    if _JWKS_CACHE["keys"] and (now - _JWKS_CACHE["fetched_at"] < JWKS_TTL_SECONDS):
        return _JWKS_CACHE["keys"]

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(JWKS_URL)
        resp.raise_for_status()
        data = resp.json()

    keys = data.get("keys", [])
    if not keys:
        raise HTTPException(status_code=500, detail="JWKS endpoint returned no keys")

    _JWKS_CACHE["keys"] = keys
    _JWKS_CACHE["fetched_at"] = now
    return keys


async def verify_access_token(token: str) -> dict:
    """
    Verifies Auth0 RS256 JWT access token using JWKS.
    Also validates issuer + audience + expiry.
    Returns token payload (claims) if valid.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token header")

    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Token header missing kid")

    jwks_keys = await _get_jwks_keys()
    jwk = next((k for k in jwks_keys if k.get("kid") == kid), None)
    if not jwk:
        raise HTTPException(status_code=401, detail="Signing key not found")

    try:
        payload = jwt.decode(
            token,
            jwk,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER,
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")


async def _fetch_userinfo(access_token: str) -> dict:
    """Fetch user profile from Auth0 User Info (includes email)."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()


async def get_current_principal(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    FastAPI dependency:
    - reads Authorization: Bearer <token>
    - verifies token
    - if email is missing from token, fetches it from Auth0 User Info
    - returns claims
    """
    payload = await verify_access_token(creds.credentials)
    if not payload.get("email"):
        try:
            userinfo = await _fetch_userinfo(creds.credentials)
            payload["email"] = userinfo.get("email") or payload.get("email")
        except Exception:
            pass  # leave email missing; route may raise 400
    return payload


def _extract_role(principal: dict) -> str:
    """Extract role from Auth0 principal. Same logic as userRoute."""
    roles_arr = principal.get("https://hiresight.local/roles")
    first_role = roles_arr[0] if isinstance(roles_arr, list) and roles_arr else None
    role = (
        (first_role if isinstance(first_role, str) else None)
        or principal.get("role")
        or principal.get("https://hiresight.ai/role")
        or "candidate"
    )
    if role not in ("admin", "recruiter", "candidate"):
        role = "candidate"
    return role


async def require_admin_or_recruiter(
    principal: dict = Depends(get_current_principal),
) -> dict:
    """
    FastAPI dependency: requires admin or recruiter role.
    Raises 403 if the user has any other role (e.g. candidate).
    Returns the principal dict for downstream use.
    """
    role = _extract_role(principal)
    if role not in ("admin", "recruiter"):
        raise HTTPException(
            status_code=403,
            detail="Forbidden. Admin or recruiter role required.",
        )
    return principal


async def require_authenticated_user(
    principal: dict = Depends(get_current_principal),
) -> dict:
    """
    FastAPI dependency: requires an authenticated user with a known role.
    Allowed roles: admin, recruiter, candidate.
    """
    role = _extract_role(principal)
    if role not in ("admin", "recruiter", "candidate"):
        raise HTTPException(status_code=403, detail="Forbidden.")
    return principal


def get_principal_role(principal: dict) -> str:
    """Public helper for route-level role-aware behavior."""
    return _extract_role(principal)
