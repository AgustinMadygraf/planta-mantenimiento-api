"""Logger con formato similar a FastAPI/Uvicorn."""

import logging
import sys

from src.shared.config import get_config


class FastAPIStyleFormatter(logging.Formatter):
    """Formateador colorizado inspirado en el output de FastAPI/Uvicorn."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def format(self, record):  # type: ignore[override]
        color = self.COLORS.get(record.levelname, self.RESET)
        fmt = f"{color}[%(asctime)s] [%(levelname)s] %(name)s: %(message)s{self.RESET}"
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        formatted = formatter.format(record)

        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            formatted += f"\n{color}{exc_text}{self.RESET}"

        return formatted


def get_logger(name: str = "planta-mantenimiento") -> logging.Logger:
    """Devuelve un logger configurado para consola."""

    config = get_config()
    log_level = str(config.get("LOG_LEVEL", "DEBUG")).upper()
    logger = logging.getLogger(name)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FastAPIStyleFormatter())
        logger.addHandler(console_handler)

        logger.setLevel(getattr(logging, log_level, logging.INFO))
        logger.propagate = False

    return logger
