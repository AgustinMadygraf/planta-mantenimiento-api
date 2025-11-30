"""Logger de consola con formato estilo Flask."""

import logging
import sys

from src.shared.config import get_config, get_is_debug


class FlaskStyleFormatter(logging.Formatter):
    """Formateador inspirado en el handler por defecto de Flask."""

    def __init__(self) -> None:
        super().__init__(
            "[%(asctime)s] %(levelname)s in %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
        )

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = super().format(record)
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            message += f"\n{exc_text}"
        return message


def get_logger(name: str = "planta-mantenimiento") -> logging.Logger:
    """Devuelve un logger configurado para consola."""

    config = get_config()
    is_debug = get_is_debug()
    log_level = "DEBUG" if is_debug else str(config.get("LOG_LEVEL", "INFO")).upper()
    logger = logging.getLogger(name)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FlaskStyleFormatter())
        logger.addHandler(console_handler)

        logger.setLevel(getattr(logging, log_level, logging.INFO))
        logger.propagate = False

    return logger


__all__ = ["get_logger", "FlaskStyleFormatter"]
