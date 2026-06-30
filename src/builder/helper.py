import os

from dotenv import load_dotenv

from src.builder import set_clients, set_config, set_service
from src.builder.clients import Clients
from src.builder.repos import Repositories
from src.builder.services import Services
from src.config.config import Config
from src.pkg import logging

logger = logging.get_logger()


if os.environ.get("APP_ENV", "") == "local":
    load_dotenv()


def fetch_config() -> Config:
    config_path = os.path.join(os.getcwd(), "config/")
    app_env = os.environ.get("APP_ENV", "prod")
    return Config.from_yaml(config_path, app_env)


def build_clients(config: Config):
    # Placeholder for building clients (e.g., database, cache)
    return (
        Clients()
        .with_ssh_client(config=config)
        .with_postgres_db_client(config=config)
        .with_redis_client(config=config)
    )


def build_service_and_repository(clients, config):
    repo = Repositories().with_vpn_repository(db_handler=clients.db_handler)
    services = Services().with_vpn_service(
        clients=clients, config=config, repo=repo.vpn_repository
    )
    return services


def fetch_and_build():
    config = fetch_config()
    clients = build_clients(config=config)
    service = build_service_and_repository(clients=clients, config=config)
    set_config(config)
    set_clients(clients)
    set_service(service)
