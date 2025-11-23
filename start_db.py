"""Crea las tablas de MySQL sin usar migraciones."""

from src.infrastructure.db.config import load_db_config
from src.infrastructure.db.models import Base
from src.infrastructure.db.session import create_engine_from_config


def main() -> None:
    config = load_db_config()
    engine = create_engine_from_config(config)
    Base.metadata.create_all(engine)
    print("Tablas creadas en", config.database)


if __name__ == "__main__":
    main()
