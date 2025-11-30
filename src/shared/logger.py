"""Compatibilidad para obtener el logger de la aplicación.

Expone ``get_logger`` desde :mod:`src.shared.logger_fastapi` para un punto
de acceso consistente.
"""

from src.shared.logger_fastapi import get_logger

__all__ = ["get_logger"]
