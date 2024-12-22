from logging.config import fileConfig
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alembic import context
from src.database.models import Base  # Import your models
from src.config.settings import DATABASE_URL  # Import your database URL

# this is the Alembic Config object
config = context.config

# Override the sqlalchemy.url from alembic.ini with the URL from settings
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata  # Use the metadata from models

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    from sqlalchemy import engine_from_config
    from sqlalchemy import pool

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
