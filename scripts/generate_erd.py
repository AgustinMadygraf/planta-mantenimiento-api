"""Generate an ER diagram from SQLAlchemy metadata.

- Uses the declarative ``Base`` metadata as source of truth by default.
- Optionally, if ``DB_URL`` is provided, connects read-only to the live
  database and reflects the schema for the diagram.

The output file defaults to ``docs/er_diagram.png`` and can be overridden
with the environment variable ``ER_OUTPUT``.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from eralchemy import render_er
except Exception as exc:  # pragma: no cover - optional dependency
    sys.stderr.write(
        "[ERD] Falta la dependencia opcional 'eralchemy2'. "
        "Instala con 'pip install eralchemy2 graphviz' y verifica que 'dot' esté en PATH.\n"
    )
    raise


def _load_metadata():
    """Return SQLAlchemy metadata either from ORM models or reflected DB."""
    db_url = os.getenv("DB_URL")
    if db_url:
        # Reflection path: build a temporary engine to mirror live schema
        from sqlalchemy import MetaData, create_engine

        engine = create_engine(db_url)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        return metadata

    # Offline path: import Declarative Base metadata
    from src.infrastructure.sqlalchemy.models import Base

    return Base.metadata


def main():
    output = Path(os.getenv("ER_OUTPUT", "docs/er_diagram.png"))
    output.parent.mkdir(parents=True, exist_ok=True)

    metadata = _load_metadata()

    try:
        render_er(metadata, str(output))
    except Exception as exc:  # pragma: no cover - rendering errors are runtime issues
        sys.stderr.write(f"[ERD] Error al generar diagrama: {exc}\n")
        raise
    else:
        print(f"[ERD] Diagrama generado en: {output}")


if __name__ == "__main__":
    main()
