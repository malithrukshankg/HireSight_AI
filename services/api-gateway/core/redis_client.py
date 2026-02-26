import logging

from redis.asyncio import Redis, from_url

from config import settings

logger = logging.getLogger(__name__)

_redis_client: Redis | None = None


async def init_redis() -> None:
    """Initialize a shared Redis client for the API process."""
    global _redis_client

    if not settings.REDIS_ENABLED:
        logger.info("Redis is disabled via REDIS_ENABLED=false")
        _redis_client = None
        return

    try:
        client = from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await client.ping()
        _redis_client = client
        logger.info("Redis connection established")
    except Exception as exc:
        _redis_client = None
        logger.warning("Redis unavailable, falling back without cache: %s", exc)


def get_redis() -> Redis | None:
    """Return the shared Redis client when available."""
    return _redis_client


async def close_redis() -> None:
    """Close the shared Redis client if it was initialized."""
    global _redis_client

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis connection closed")
