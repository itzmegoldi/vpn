from pydantic import BaseModel

from src.config.database import DatabaseConfig, RedisConfig
from src.pkg.config import ConfigMixing


class ServerAuthConfig(BaseModel):
    client_name: str
    client_key: str


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    auth: list[ServerAuthConfig]


class Config(BaseModel, ConfigMixing):
    app_env: str = "local"
    server: ServerConfig
    database: DatabaseConfig
    redis: RedisConfig
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
