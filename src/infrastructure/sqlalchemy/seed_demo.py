"""Helper to seed demo users idempotently."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from src.infrastructure.sqlalchemy.user_repository import SqlAlchemyUserRepository
from src.infrastructure.user_repository import DEFAULT_DEMO_USERS
from src.shared.logger import get_logger

logger = get_logger("seed_demo_users")


def seed_demo_users(repo: SqlAlchemyUserRepository) -> int:
    """Create default demo users if they do not exist.

    Returns:
        int: number of users created.
    """

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
        except SQLAlchemyError as exc:
            logger.error(
                "No se pudo crear el usuario %s por error de base de datos",
                user["username"],
                exc_info=exc,
            )
        except ValueError as exc:
            logger.error(
                "No se pudo crear el usuario %s por error de valor inesperado",
                user["username"],
                exc_info=exc,
            )
    return created


__all__ = ["seed_demo_users"]
