import json
from collections.abc import AsyncIterator
from typing import Any

from src.config.database import RedisConfig


class RedisClient:
    def __init__(self, config: RedisConfig):
        try:
            import redis
            import redis.asyncio as async_redis
        except ImportError as exc:
            raise RuntimeError(
                "redis package is required. Install dependencies from requirements.txt."
            ) from exc

        self.config = config
        self.client = redis.Redis(
            host=config.host,
            port=int(config.port),
            password=config.password,
            decode_responses=True,
            socket_timeout=None,
            socket_connect_timeout=10,
            health_check_interval=30,
        )
        self.async_client = async_redis.Redis(
            host=config.host,
            port=int(config.port),
            password=config.password,
            decode_responses=True,
            socket_timeout=None,
            socket_connect_timeout=10,
            health_check_interval=30,
        )

    async def increment_with_expiry(self, key: str, expiry_seconds: int) -> int:
        async with self.async_client.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, expiry_seconds)
            count, _ = await pipe.execute()
        return int(count)

    async def produce_message(
        self, message: dict[str, Any], queue_name: str | None = None
    ) -> int:
        queue = queue_name or self.config.queue_name
        return await self.async_client.rpush(queue, json.dumps(message))

    async def consume_messages(
        self, queue_name: str | None = None, timeout: int = 0
    ) -> AsyncIterator[dict[str, Any]]:
        queue = queue_name or self.config.queue_name
        while True:
            item = await self.async_client.blpop(queue, timeout=timeout)
            if item is None:
                continue
            _, raw_message = item
            yield json.loads(raw_message)

    def test_connection(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            return False

    async def async_test_connection(self) -> bool:
        try:
            return await self.async_client.ping()
        except Exception:
            return False

    async def close(self):
        await self.async_client.aclose()
        self.client.close()
