"""Punto de entrada retrocompatible para los modelos ORM.

Los modelos fueron movidos a `src/interface_adapters/gateways/sqlalchemy/models.py`
como parte de la separación entre infraestructura y gateways. Se reexportan
para mantener compatibilidad con scripts existentes.
"""

from src.interface_adapters.gateways.sqlalchemy.models import (
    AreaModel,
    Base,
    EquipmentModel,
    PlantModel,
    SystemModel,
)

__all__ = ["Base", "PlantModel", "AreaModel", "EquipmentModel", "SystemModel"]
