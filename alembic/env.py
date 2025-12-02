"""Alembic environment configured to reuse the project's SQLAlchemy metadata."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.infrastructure.sqlalchemy.config import load_db_config
from src.infrastructure.sqlalchemy.models import Base
from src.infrastructure.sqlalchemy.session import create_engine_from_config
from src.shared.logger import get_logger

# Alembic Config object, provides access to values within alembic.ini
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = get_logger("alembic.env")
target_metadata = Base.metadata


def _configure_sqlalchemy_url() -> None:
    "Inject DB URL so Alembic CLI commands work without manual flags."
    try:
        db_config = load_db_config()
    except RuntimeError as exc:
        logger.error("No se pudo cargar configuracion de DB para Alembic", exc_info=exc)
        raise
    config.set_main_option("sqlalchemy.url", db_config.url)


def run_migrations_offline() -> None:
    "Run migrations without a live DB connection."
    _configure_sqlalchemy_url()
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    "Run migrations using an Engine built from existing config helpers."
    _configure_sqlalchemy_url()
    db_config = load_db_config()
    connectable = create_engine_from_config(db_config)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
