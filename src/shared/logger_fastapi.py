"""
Path: src/shared/logger_fastapi.py
"""

import logging
import sys
from src.shared.config import get_config

class FastAPIStyleFormatter(logging.Formatter):
    "Formateador de logs con estilo FastAPI/Uvicorn"
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m', # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        fmt = f"{color}[%(asctime)s] [%(levelname)s] %(name)s: %(message)s{self.RESET}"
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        formatted = formatter.format(record)

        # Agregar excepción formateada si existe
        if record.exc_info:
            # Mantener el formato de excepción al estilo FastAPI
            exc_text = self.formatException(record.exc_info)
            formatted += f"\n{color}{exc_text}{self.RESET}"

        return formatted

def get_logger(name="api-woocommerce"):
    "Configura y devuelve un logger con formato estilo FastAPI/Uvicorn."
    config = get_config()
    log_level = config.get("LOG_LEVEL", "DEBUG").upper()
    logger = logging.getLogger(name)

    # Evitar agregar handlers duplicados
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)  # FastAPI/Uvicorn usa stdout
        console_handler.setFormatter(FastAPIStyleFormatter())
        logger.addHandler(console_handler)

        # Configurar nivel de log
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        # Evitar propagación para evitar duplicados
        logger.propagate = False

    return logger
