"""Pydantic schemas para entradas y salidas de los adaptadores HTTP."""

from .area import AreaCreate, AreaUpdate
from .auth import LoginRequest
from .equipment import EquipmentCreate, EquipmentUpdate
from .plant import PlantCreate, PlantUpdate
from .system import SystemCreate, SystemUpdate

__all__ = [
    "PlantCreate",
    "PlantUpdate",
    "AreaCreate",
    "AreaUpdate",
    "EquipmentCreate",
    "EquipmentUpdate",
    "SystemCreate",
    "SystemUpdate",
    "LoginRequest",
]
