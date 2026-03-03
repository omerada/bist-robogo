# Source: Doc 07 §14 — Rate Limiter
"""Redis tabanlı sliding window rate limiter."""

from app.core.redis_client import redis_manager


async def check_rate_limit(key: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
    """Sliding window rate limit kontrolü.

    Args:
        key: Rate limit anahtarı (genelde IP veya user_id)
        max_requests: Pencere içinde izin verilen maksimum istek
        window_seconds: Pencere süresi (saniye)

    Returns:
        bool: True ise istek izinli, False ise limit aşılmış
    """
    if redis_manager.client is None:
        return True

    redis_key = f"rate:limit:{key}"

    try:
        current = await redis_manager.client.incr(redis_key)
        if current == 1:
            await redis_manager.client.expire(redis_key, window_seconds)
        return current <= max_requests
    except Exception:
        # Redis erişilemiyorsa izin ver (fail-open)
        return True
