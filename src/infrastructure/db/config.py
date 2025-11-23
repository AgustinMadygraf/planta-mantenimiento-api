"""Configuración de conexión a base de datos MySQL."""

from dataclasses import dataclass
import os
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


def load_db_config() -> DBConfig:
    """Lee las variables de entorno y devuelve una configuración inmutable."""

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
