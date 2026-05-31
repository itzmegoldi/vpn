from src.pkg.database.db import PostgresDatabase
from src.pkg.database.interface import IDatabase
from src.pkg.interfaces import IRedisClient, ISSHClient
from src.pkg.redis import RedisClient
from src.pkg.ssh import SSHClient


class Clients:

    def with_postgres_db_client(self, config) -> IDatabase:
        self.db_handler: IDatabase = PostgresDatabase(config.database)
        return self

    def with_redis_client(self, config) -> "Clients":
        self.redis_client: IRedisClient = RedisClient(config.redis)
        return self

    def with_ssh_client(self, config) -> ISSHClient:
        self.ssh_client: ISSHClient = SSHClient()
        return self

    def new_ssh_client(self) -> ISSHClient:
        return SSHClient()
