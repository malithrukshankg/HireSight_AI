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


async def get_current_principal(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    FastAPI dependency:
    - reads Authorization: Bearer <token>
    - verifies token
    - returns claims
    """
    return await verify_access_token(creds.credentials)
