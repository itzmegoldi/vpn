import os
import ssl

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.database import DatabaseConfig, RedisConfig


class PostgresDatabase:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        engine_kwargs = {
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
        if self.config.ssl is not None:
            engine_kwargs["connect_args"] = {
                "sslmode": self.config.ssl.sslmode,
                "sslcert": f"{os.getcwd()}/{self.config.ssl.sslcertpath}",
            }
        sync_url: str = (
            f"postgresql://{config.user}:{config.password}@{config.url}:{config.port}/{config.name}"
        )
        self.engine = create_engine(sync_url, **engine_kwargs)

        async_engine_kwargs = {
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
        if self.config.ssl is not None:
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context.load_cert_chain(
                certfile=f"{os.getcwd()}/{self.config.ssl.sslcertpath}"
            )
            async_engine_kwargs["connect_args"] = {"ssl": ssl_context}

        async_url = f"postgresql+asyncpg://{config.user}:{config.password}@{config.url}:{config.port}/{config.name}"
        self.async_engine = create_async_engine(async_url, **async_engine_kwargs)

    def get_session(self) -> Session:
        local_session = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )
        return local_session()

    async def get_async_session(self) -> AsyncSession:
        async_session = async_sessionmaker(
            bind=self.async_engine, autocommit=False, autoflush=False
        )
        return async_session()
