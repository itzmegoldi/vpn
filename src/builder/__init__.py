from typing import Optional

from src.builder.clients import Clients
from src.builder.services import Services

from src.config.config import Config

_config: Optional[Config] = None
_clients: Optional[Clients] = None
_service: Optional[Services] = None


def set_config(config: Config):
    global _config
    _config = config


def get_config() -> Config:

    if _config is None:
        raise ValueError("Config not set")
    return _config


def set_clients(clients: Clients):
    global _clients
    _clients = clients


def get_clients() -> Clients:
    if _clients is None:
        raise ValueError("Clients not set")
    return _clients


def set_service(service: Services):
    global _service
    _service = service


def get_service() -> Services:
    if _service is None:
        raise ValueError("Service not set")
    return _service
