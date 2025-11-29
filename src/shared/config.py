"""Utilidades de configuración y carga de entorno.

Centraliza la lectura de variables de entorno y proporciona defaults
seguros para el proyecto. Tolera la ausencia de `.env` y permite
sobrescribir valores desde el entorno del sistema.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependencia opcional
    load_dotenv = None
except Exception as exc:  # pragma: no cover - visibiliza fallos inesperados de importación
    logger.exception("Error inesperado importando python-dotenv")
    raise


def load_env(env_path: str = ".env") -> bool:
    """Carga variables desde un archivo `.env` si existe.

    Devuelve `True` si el archivo se cargó exitosamente, `False` si no
    existe y propaga una `RuntimeError` para errores de lectura. Usa
    `python-dotenv` cuando está instalado; de lo contrario aplica un
    parser mínimo compatible con `KEY=value`.
    """

    path = Path(env_path)

    if not path.exists():
        return False

    if load_dotenv is not None:
        try:
            return load_dotenv(path, override=False)
        except (OSError, UnicodeError) as exc:
            raise RuntimeError(f"No se pudo cargar {env_path}: {exc}") from exc
        except Exception as exc:  # pragma: no cover - visibiliza fallos inesperados
            logger.exception("Carga fallida de %s con python-dotenv", env_path)
            raise

    # Fallback manual sin dependencias externas
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except OSError as exc:
        raise RuntimeError(f"No se pudo leer {env_path}: {exc}") from exc

    return True


def get_env(var_name: str, default: Optional[str] = None) -> Optional[str]:
    """Obtiene una variable de entorno con default opcional."""

    return os.environ.get(var_name, default)


def _int_or_default(value: Optional[str], default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError as exc:
        raise RuntimeError(
            "Valor numérico inválido en configuración (.env o variables del sistema)."
        ) from exc


def get_mysql_config() -> Dict[str, Any]:
    """Devuelve un diccionario con la configuración de MySQL.

    Acepta variables prefijadas como `DB_*` o `MYSQL_*` y aplica valores
    por defecto cuando están ausentes.
    """

    return {
        "host": get_env("DB_HOST") or get_env("MYSQL_HOST", "localhost"),
        "port": _int_or_default(get_env("DB_PORT") or get_env("MYSQL_PORT"), 3306),
        "user": get_env("DB_USER") or get_env("MYSQL_USER", "root"),
        "password": get_env("DB_PASSWORD") or get_env("MYSQL_PASSWORD", ""),
        "database": get_env("DB_NAME")
        or get_env("MYSQL_DB")
        or get_env("MYSQL_DATABASE", "planta_mantenimiento"),
        "pool_size": _int_or_default(get_env("DB_POOL_SIZE"), 5),
        "max_overflow": _int_or_default(get_env("DB_MAX_OVERFLOW"), 10),
        "pool_timeout": _int_or_default(get_env("DB_POOL_TIMEOUT"), 30),
        "pool_recycle": _int_or_default(get_env("DB_POOL_RECYCLE"), 1800),
        "echo": str(get_env("DB_ECHO", "false")).lower() in {"1", "true", "yes"},
    }


def get_use_db() -> Optional[str]:
    return get_env("USE_DB")


def get_static_path() -> str:
    return get_env("STATIC_PATH", "static")


def get_config() -> Dict[str, Any]:
    """Carga configuración general desde variables de entorno."""

    return {
        "LOG_LEVEL": get_env("LOG_LEVEL", "DEBUG"),
        "URL": get_env("URL"),
        "CK": get_env("CK"),
        "CS": get_env("CS"),
        "MYSQL_HOST": get_env("MYSQL_HOST"),
        "MYSQL_PORT": get_env("MYSQL_PORT"),
        "MYSQL_USER": get_env("MYSQL_USER"),
        "MYSQL_PASSWORD": get_env("MYSQL_PASSWORD"),
        "MYSQL_DATABASE": get_env("MYSQL_DATABASE"),
        "API_BASE": get_env("API_BASE"),
        "CORS_ORIGINS": get_env("CORS_ORIGINS"),
    }


def get_cors_origins(default: str = "http://localhost:5173") -> list[str]:
    """Devuelve una lista de orígenes permitidos para CORS."""

    origins = get_env("CORS_ORIGINS")

    if not origins:
        return [default]

    return [origin.strip() for origin in origins.split(",") if origin.strip()]
