from src.builder import set_clients, set_config, set_service
from src.builder.clients import Clients
from src.builder.repos import Repositories
from src.builder.services import Services
from src.config.settings import AppConfig
from src.pkg import logging

logger = logging.get_logger()


def build_config() -> AppConfig:
    return AppConfig()


def build_clients(config: AppConfig):
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
    config = build_config()
    clients = build_clients(config=config)
    service = build_service_and_repository(clients=clients, config=config)
    set_config(config)
    set_clients(clients)
    set_service(service)


def fetch_config() -> AppConfig:
    logger.info("Fetching configuration...")
    config = AppConfig()
    return config
