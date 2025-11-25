"""Helpers to build SQLAlchemy engines and sessions."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.infrastructure.sqlalchemy.config import DBConfig


def create_engine_from_config(config: DBConfig) -> Engine:
    """Construct an Engine with sensible pooling defaults."""

    return create_engine(
        config.url,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
        pool_recycle=config.pool_recycle,
        echo=config.echo,
        future=True,
    )


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a session factory to produce short-lived sessions per request."""

    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)
