from pydantic_settings import BaseSettings
from src.config.database import DatabaseConfig, RedisConfig


class AppConfig(BaseSettings):
    app_env: str = "local"
    server_host: str = "0.0.0.0"
    server_port: int = 8080
    database_url: str
    database_port: str = "5432"
    database_name: str
    database_user: str
    database_password: str
    redis_host: str
    redis_port: int
    redis_password: str | None = None
    redis_queue_name: str = "vpn_worker_queue"
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    @property
    def database(self) -> DatabaseConfig:
        return DatabaseConfig(
            url=self.database_url,
            port=self.database_port,
            name=self.database_name,
            user=self.database_user,
            password=self.database_password,
        )

    @property
    def redis(self) -> RedisConfig:
        return RedisConfig(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            queue_name=self.redis_queue_name,
        )

    class Config:
        env_file = ".env"
