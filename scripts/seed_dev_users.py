"""Inserta usuarios de demostración para entornos de desarrollo."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from src.infrastructure.sqlalchemy.config import load_db_config
from src.infrastructure.sqlalchemy.session import (
    SessionFactory,
    build_session_factory,
    create_engine_from_config,
)
from src.infrastructure.sqlalchemy.user_repository import SqlAlchemyUserRepository
from src.infrastructure.user_repository import DEFAULT_DEMO_USERS
from src.shared.logger import get_logger

logger = get_logger("seed-users")


def _build_repo() -> SqlAlchemyUserRepository:
    config = load_db_config()
    engine = create_engine_from_config(config)
    session_factory: SessionFactory = build_session_factory(engine)
    return SqlAlchemyUserRepository(session_factory)


def main() -> None:
    "Puebla la base de datos con usuarios de demostración."
    logger.info("Cargando usuarios de demostración en la base de datos…")
    try:
        repo = _build_repo()
    except RuntimeError as exc:
        logger.error("No se pudo cargar la configuración de base de datos", exc_info=exc)
        raise

    created = 0
    for user in DEFAULT_DEMO_USERS:
        existing = repo.get_by_username(user["username"])
        if existing:
            logger.info("Usuario %s ya existe, se omite", user["username"])
            continue

        try:
            repo.create_user(
                username=user["username"],
                password=user["password"],
                role=user["role"],
                areas=user["areas"],
                equipos=user["equipos"],
            )
            created += 1
            logger.info("Usuario %s creado", user["username"])
        except SQLAlchemyError as exc:  # pragma: no cover - script auxiliar
            logger.error("No se pudo crear el usuario %s", user["username"], exc_info=exc)
            raise

    logger.info("Usuarios procesados. Nuevos: %s", created)


if __name__ == "__main__":
    main()
