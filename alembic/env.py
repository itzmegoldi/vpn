import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv

from sqlalchemy import create_engine
from src.models.base import BaseModel
from src.models.vpn import VPNClient, VPNServer

load_dotenv()


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BaseModel.metadata

MODEL = dict(
    VPNClient=VPNClient,
    VPNServer=VPNServer,
)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        raise ValueError("Database URL is not configured.")
    url_token = {
        "DATABASE_USER": os.getenv("DATABASE_USER"),
        "DATABASE_PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "DATABASE_HOST": os.getenv("DATABASE_URL"),
        "DATABASE_PORT": os.getenv("DATABASE_PORT"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
    }
    url = url.format(**url_token)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        raise ValueError("Database URL is not configured.")
    url_token = {
        "DATABASE_USER": os.getenv("DATABASE_USER"),
        "DATABASE_PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "DATABASE_HOST": os.getenv("DATABASE_URL"),
        "DATABASE_PORT": os.getenv("DATABASE_PORT"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
    }
    url = url.format(**url_token)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        dialect_opts={"paramstyle": "named"},
    )
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
