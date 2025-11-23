"""Crea las tablas de MySQL sin usar migraciones."""

import sys

from sqlalchemy.exc import OperationalError, SQLAlchemyError

from src.infrastructure.db.config import load_db_config
from src.infrastructure.db.models import Base
from src.infrastructure.db.session import create_engine_from_config
from src.shared.logger_fastapi import get_logger

logger = get_logger("start_db")


def main() -> None:
    try:
        config = load_db_config()
    except RuntimeError as exc:  # problemas al leer .env o castear valores
        logger.error(
            "No se pudo cargar la configuración de base de datos. Revisa que exista el archivo .env"
            " o que los valores DB_* sean válidos.",
            exc_info=exc,
        )
        sys.exit(1)

    engine = create_engine_from_config(config)

    try:
        Base.metadata.create_all(engine)
        logger.info("Tablas creadas en %s", config.database)
    except OperationalError as exc:  # credenciales/host/puerto incorrectos
        logger.error(
            "No se pudo conectar a MySQL. Verifica DB_USER, DB_PASSWORD, DB_HOST y privilegios.",
            exc_info=exc,
        )
        sys.exit(1)
    except SQLAlchemyError as exc:  # otros problemas de driver o DDL
        logger.error("Error creando tablas:", exc_info=exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
