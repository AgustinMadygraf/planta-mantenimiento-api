"""Configuración de conexión a base de datos MySQL."""

from dataclasses import dataclass
import os
from pathlib import Path
from urllib.parse import quote_plus


@dataclass(frozen=True, slots=True)
class DBConfig:
    """Valores necesarios para crear el engine de SQLAlchemy."""

    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "planta_mantenimiento"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    echo: bool = False

    @property
    def url(self) -> str:
        """URL de conexión en formato mysql+pymysql."""

        encoded_password = quote_plus(self.password)
        return (
            f"mysql+pymysql://{self.user}:{encoded_password}@{self.host}:{self.port}/"
            f"{self.database}"
        )


def _load_env_file(env_path: str = ".env") -> None:
    """Carga un archivo .env básico en `os.environ` si existe.

    Evita añadir dependencias externas y tolera la ausencia del archivo. Si no
    puede leerse, se lanza un RuntimeError para que la capa de infraestructura
    pueda notificar al usuario.
    """

    path = Path(env_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró {env_path}")

    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except OSError as exc:  # problemas de permisos, encoding o disco
        raise RuntimeError(f"No se pudo leer {env_path}: {exc}") from exc


def load_db_config() -> DBConfig:
    """Lee las variables de entorno y devuelve una configuración inmutable."""

    try:
        _load_env_file()
    except FileNotFoundError:
        # No es un error fatal: se usan variables de entorno del sistema o defaults.
        pass
    except RuntimeError as exc:
        raise RuntimeError(
            "No se pudieron cargar variables desde .env. Revisa permisos o encoding."
        ) from exc

    try:
        return DBConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "planta_mantenimiento"),
            pool_size=int(os.getenv("DB_POOL_SIZE", 5)),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 10)),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", 30)),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", 1800)),
            echo=os.getenv("DB_ECHO", "false").lower() in {"1", "true", "yes"},
        )
    except ValueError as exc:
        raise RuntimeError(
            "Variables de entorno DB_* inválidas. Asegúrate de que los valores numéricos"
            " sean enteros (por ejemplo DB_PORT, DB_POOL_SIZE)."
        ) from exc
