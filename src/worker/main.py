import asyncio

from paramiko import client

from src.builder import get_clients, get_config
from src.builder.helper import fetch_and_build
from src.pkg import logging
from src.worker.consumer import process_message

logging.configure_logger(default_logger_names=["root", "worker"])
logger = logging.get_logger()

from redis.asyncio import Redis


async def run_consumer():
    fetch_and_build()
    config = get_config()
    redis_client = get_clients().redis_client

    logger.info("Worker consumer started", context={"queue": config.redis.queue_name})
    conn = await redis_client.async_test_connection()
    logger.info("Redis connection test", context={"success": conn})
    async for message in redis_client.consume_messages(config.redis.queue_name):
        try:
            await process_message(message)
        except Exception as exc:
            logger.error("Worker message failed", context={"error": str(exc)})


async def run_tester():
    fetch_and_build()
    config = get_config()
    async_client = Redis(
        host=config.redis.host,
        port=int(config.redis.port),
        password=config.redis.password,
        decode_responses=True,
        socket_timeout=None,
        socket_connect_timeout=5,
    )

    print(await async_client.ping())
    print("Waiting...")

    while True:
        item = await async_client.blpop("vpn_worker_queue", timeout=0)
        logger.info("Received message", context={"message": item})


if __name__ == "__main__":
    asyncio.run(run_consumer())
