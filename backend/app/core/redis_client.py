# Source: Doc 07 §13 — Redis Yönetimi
"""Redis bağlantı yöneticisi."""

import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()


class RedisManager:
    """Redis bağlantısını yönetir. Uygulama başlangıcında connect(), kapanışta disconnect() çağrılır."""

    def __init__(self) -> None:
        self.client: redis.Redis | None = None

    async def connect(self) -> None:
        """Redis'e bağlan."""
        self.client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await self.client.ping()

    async def disconnect(self) -> None:
        """Redis bağlantısını kapat."""
        if self.client:
            await self.client.close()

    async def get_cached(self, key: str) -> str | None:
        """Cache'ten veri oku."""
        if self.client is None:
            return None
        return await self.client.get(key)

    async def set_cached(self, key: str, value: str, ttl: int | None = None) -> None:
        """Cache'e veri yaz."""
        if self.client is None:
            return
        ttl = ttl or settings.REDIS_CACHE_TTL
        await self.client.set(key, value, ex=ttl)

    async def delete_cached(self, key: str) -> None:
        """Cache'ten veri sil."""
        if self.client is None:
            return
        await self.client.delete(key)

    async def publish(self, channel: str, message: str) -> None:
        """Pub/Sub mesaj gönder."""
        if self.client is None:
            return
        await self.client.publish(channel, message)


# Singleton instance
redis_manager = RedisManager()
