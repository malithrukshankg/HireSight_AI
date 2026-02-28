import hashlib
import json
import logging
from collections.abc import Mapping
from typing import Any

from config import settings
from core.redis_client import get_redis

logger = logging.getLogger(__name__)


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _params_fingerprint(params: Mapping[str, Any] | None) -> str:
    if not params:
        return "no_params"
    payload = _json_dumps(dict(params))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def build_cache_key(
    domain: str,
    resource: str,
    *,
    scope: str | None = None,
    version: int | None = None,
    params: Mapping[str, Any] | None = None,
) -> str:
    """Build a deterministic namespaced cache key."""
    parts = [settings.REDIS_KEY_PREFIX, domain, resource]
    if scope:
        parts.append(scope)
    if version is not None:
        parts.append(f"v{version}")
    parts.append(_params_fingerprint(params))
    return ":".join(parts)


def build_version_key(domain: str, resource: str) -> str:
    """Build key for namespace version counters."""
    return ":".join([settings.REDIS_KEY_PREFIX, domain, resource, "version"])


async def get_json(key: str) -> Any | None:
    """Get and decode JSON payload from Redis."""
    redis = get_redis()
    if redis is None:
        return None

    try:
        raw = await redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Redis get_json failed for key '%s': %s", key, exc)
        return None


async def set_json(key: str, value: Any, ttl_seconds: int | None = None) -> bool:
    """Encode and store JSON payload in Redis."""
    redis = get_redis()
    if redis is None:
        return False

    ttl = ttl_seconds if ttl_seconds is not None else settings.REDIS_DEFAULT_TTL_SECONDS
    try:
        payload = _json_dumps(value)
        await redis.set(key, payload, ex=ttl)
        return True
    except Exception as exc:
        logger.warning("Redis set_json failed for key '%s': %s", key, exc)
        return False


async def incr_counter(key: str, amount: int = 1) -> int | None:
    """Increment a Redis integer counter and return the new value."""
    redis = get_redis()
    if redis is None:
        return None

    try:
        return int(await redis.incrby(key, amount))
    except Exception as exc:
        logger.warning("Redis incr_counter failed for key '%s': %s", key, exc)
        return None


async def get_counter(key: str, default: int = 1) -> int:
    """Read a Redis integer counter with an in-memory default fallback."""
    redis = get_redis()
    if redis is None:
        return default

    try:
        raw = await redis.get(key)
        if raw is None:
            return default
        return int(raw)
    except Exception as exc:
        logger.warning("Redis get_counter failed for key '%s': %s", key, exc)
        return default
