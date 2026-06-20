from src.config.database import DatabaseConfig, RedisConfig
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
import os
import ssl


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
        self.engine = create_engine(
            self.config.sync_url,
            **engine_kwargs
        )

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
        self.async_engine = create_async_engine(
            self.config.async_url,
            **async_engine_kwargs
        )

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
