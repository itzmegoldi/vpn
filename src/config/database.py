from pydantic import BaseModel
from typing import Optional


class DatabaseSslConfig(BaseModel):
    sslmode: str = "verify-full"
    sslcertpath: str


class DatabaseConfig(BaseModel):
    url: str
    port: str
    name: str
    user: str
    password: str

    ssl: Optional[DatabaseSslConfig] = None

    @property
    def sync_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.url}:{self.port}/{self.name}"

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.url}:{self.port}/{self.name}"


class RedisConfig(BaseModel):
    host: str
    port: int
    password: str | None = None
    queue_name: str = "vpn_worker_queue"

    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}"
        return f"redis://{self.host}:{self.port}"

    @property
    def async_url(self) -> str:
        return self.url

    @property
    def sync_url(self) -> str:
        return self.url
