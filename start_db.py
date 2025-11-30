"""
Path: start_db.py
Crea las tablas de MySQL sin usar migraciones.
"""

import sys

from sqlalchemy.exc import OperationalError, SQLAlchemyError
import pymysql
from src.infrastructure.sqlalchemy.session import build_session_factory
from src.infrastructure.sqlalchemy.user_repository import SqlAlchemyUserRepository
from src.infrastructure.user_repository import DEFAULT_DEMO_USERS
from src.infrastructure.sqlalchemy.config import load_db_config
from src.infrastructure.sqlalchemy.models import Base
from src.infrastructure.sqlalchemy.session import create_engine_from_config
from src.shared.logger import get_logger

logger = get_logger("start_db")


def main() -> None:
    "Crea las tablas en la base de datos MySQL según los modelos definidos."

    try:
        config = load_db_config()
    except RuntimeError as exc:
        logger.error(
            "No se pudo cargar la configuración de base de datos. Revisa que exista el archivo .env o que los valores DB_* sean válidos.",
            exc_info=exc,
        )
        sys.exit(1)

    engine = create_engine_from_config(config)

    def create_tables():
        try:
            Base.metadata.create_all(engine)
            logger.info("Tablas creadas en %s", config.database)
            return True
        except OperationalError as exc:
            # Si la base de datos no existe, devolver el error para manejarlo en main
            return exc
        except SQLAlchemyError as exc:
            logger.error("Error creando tablas:", exc_info=exc)
            return False

    result = create_tables()
    if result is True:
        pass  # Tablas creadas correctamente
    elif isinstance(result, OperationalError):
        exc = result
        if hasattr(exc.orig, 'args') and exc.orig.args and exc.orig.args[0] == 1049:
            logger.warning("La base de datos '%s' no existe. Creando...", config.database)
            try:
                conn = pymysql.connect(
                    host=config.host,
                    port=config.port,
                    user=config.user,
                    password=config.password,
                )
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                conn.commit()
                conn.close()
                logger.info("Base de datos '%s' creada correctamente.", config.database)
            except pymysql.MySQLError as db_exc:
                logger.error("No se pudo crear la base de datos.", exc_info=db_exc)
                sys.exit(1)
            # Reintentar la creación de tablas
            engine = create_engine_from_config(config)
            result2 = create_tables()
            if result2 is not True:
                logger.error("Error creando tablas tras crear la base de datos.")
                sys.exit(1)
        else:
            logger.error(
                "No se pudo conectar a MySQL. Verifica DB_USER, DB_PASSWORD, DB_HOST y privilegios.",
                exc_info=exc,
            )
            sys.exit(1)
    else:
        sys.exit(1)

    try:

        session_factory = build_session_factory(engine)
        repo = SqlAlchemyUserRepository(session_factory)
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
                logger.error("No se pudo crear el usuario %s por error de base de datos", user["username"], exc_info=exc)
            except ValueError as exc:
                logger.error("No se pudo crear el usuario %s por error de valor inesperado", user["username"], exc_info=exc)
        logger.info("Usuarios procesados. Nuevos: %s", created)
    except (SQLAlchemyError, ValueError) as exc:
        logger.error("Error al poblar usuarios de demostración", exc_info=exc)


if __name__ == "__main__":
    main()
