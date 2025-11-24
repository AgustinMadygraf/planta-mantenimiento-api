"""Configuración de conexión a base de datos MySQL."""

from dataclasses import dataclass

from src.shared.config import get_mysql_config, load_env


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

        # Lazy import para evitar dependencia si no se usa MySQL
        from urllib.parse import quote_plus

        encoded_password = quote_plus(self.password)
        return (
            f"mysql+pymysql://{self.user}:{encoded_password}@{self.host}:{self.port}/"
            f"{self.database}"
        )


def load_db_config() -> DBConfig:
    """Lee variables de entorno (o `.env`) y devuelve una configuración inmutable.

    Tolerante a la ausencia de `.env` y capaz de detectar valores numéricos
    inválidos para avisar temprano a la capa de infraestructura.
    """

    try:
        load_env()
    except RuntimeError as exc:
        raise RuntimeError(
            "No se pudieron cargar variables desde .env. Revisa permisos o encoding."
        ) from exc

    values = get_mysql_config()

    try:
        return DBConfig(
            host=values["host"] or "localhost",
            port=int(values["port"]),
            user=values["user"] or "root",
            password=values["password"] or "",
            database=values["database"] or "planta_mantenimiento",
            pool_size=int(values["pool_size"]),
            max_overflow=int(values["max_overflow"]),
            pool_timeout=int(values["pool_timeout"]),
            pool_recycle=int(values["pool_recycle"]),
            echo=bool(values["echo"]),
        )
    except (TypeError, ValueError, RuntimeError) as exc:
        raise RuntimeError(
            "Variables de entorno DB_* inválidas. Asegúrate de que los valores numéricos sean enteros"
            " (por ejemplo DB_PORT, DB_POOL_SIZE)."
        ) from exc
