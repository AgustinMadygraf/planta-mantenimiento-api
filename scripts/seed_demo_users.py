"""Script de conveniencia para poblar usuarios demo tras aplicar migraciones."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infrastructure.sqlalchemy.config import load_db_config
from src.infrastructure.sqlalchemy.seed_demo import seed_demo_users
from src.infrastructure.sqlalchemy.session import (
    build_session_factory,
    create_engine_from_config,
)
from src.infrastructure.sqlalchemy.user_repository import SqlAlchemyUserRepository


def main() -> None:
    """Crea usuarios demo si no existen en la base determinada por .env."""

    config = load_db_config()
    engine = create_engine_from_config(config)
    session_factory = build_session_factory(engine)

    repo = SqlAlchemyUserRepository(session_factory)
    created = seed_demo_users(repo)
    print(f"Usuarios procesados. Nuevos: {created}")


if __name__ == "__main__":
    main()
