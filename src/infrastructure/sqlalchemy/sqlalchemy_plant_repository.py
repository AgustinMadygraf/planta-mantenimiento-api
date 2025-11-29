"""Ubicación retrocompatible del repositorio SQLAlchemy.

La implementación real vive en
`src/interface_adapters/gateways/sqlalchemy/plant_repository.py` para respetar
los principios de Arquitectura Limpia. Este módulo solo reexporta la clase para
no romper imports existentes durante la migración.
"""

from src.interface_adapters.gateways.sqlalchemy.plant_repository import (
    SqlAlchemyPlantRepository,
)

__all__ = ["SqlAlchemyPlantRepository"]
