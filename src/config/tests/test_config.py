import os

import pytest

from src.builder.helper import fetch_config

from src.config.config import Config, ServerAuthConfig, ServerConfig
from src.config.database import DatabaseConfig, RedisConfig


@pytest.fixture
def database_config():
    return DatabaseConfig(
        url="localhost",
        port="5432",
        user="test_user",
        password="test_password",
        name="test_db",
    )


@pytest.fixture
def redis_config():
    return RedisConfig(
        host="localhost",
        port="6379",
        password="test_password",
        queue_name="vpn_worker_queue_test",
    )


@pytest.fixture
def expected_config(database_config, redis_config):
    return Config(
        server=ServerConfig(
            host="localhost",
            port=8080,
            auth=[ServerAuthConfig(client_name="test_client", client_key="test_key")],
        ),
        database=database_config,
        redis=redis_config,
        rate_limit_requests=60,
        rate_limit_window_seconds=60,
    )


def test_config_loading(expected_config):
    os.environ.update({"APP_ENV": "test"})
    config = fetch_config()
    assert config.server == expected_config.server
    assert config.database == expected_config.database
    assert config.redis == expected_config.redis
    assert config.rate_limit_requests == expected_config.rate_limit_requests
    assert config.rate_limit_window_seconds == expected_config.rate_limit_window_seconds
