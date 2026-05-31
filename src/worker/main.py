import asyncio

from src.builder import get_clients, get_config
from src.builder.helper import fetch_and_build
from src.pkg import logging
from src.worker.consumer import process_message

logging.configure_logger(default_logger_names=["root", "worker"])
logger = logging.get_logger()


async def run_consumer():
    fetch_and_build()
    config = get_config()
    redis_client = get_clients().redis_client

    logger.info("Worker consumer started", context={"queue": config.redis.queue_name})
    async for message in redis_client.consume_messages(config.redis.queue_name):
        try:
            await process_message(message)
        except Exception as exc:
            logger.error("Worker message failed", context={"error": str(exc)})


if __name__ == "__main__":
    asyncio.run(run_consumer())
