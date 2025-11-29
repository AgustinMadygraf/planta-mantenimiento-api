"""Funciones de mapeo entre modelos ORM y entidades de dominio."""

from src.entities.area import Area
from src.entities.equipment import Equipment
from src.entities.plant import Plant
from src.entities.system import System
from src.interface_adapters.gateways.sqlalchemy.models import (
    AreaModel,
    EquipmentModel,
    PlantModel,
    SystemModel,
)


def plant_to_entity(model: PlantModel) -> Plant:
    return Plant(
        id=model.id,
        name=model.name,
        location=model.location or "",
        status=model.status,
    )


def area_to_entity(model: AreaModel) -> Area:
    return Area(
        id=model.id,
        plant_id=model.plant_id,
        name=model.name,
        status=model.status,
    )


def equipment_to_entity(model: EquipmentModel) -> Equipment:
    return Equipment(
        id=model.id,
        area_id=model.area_id,
        name=model.name,
        status=model.status,
    )


def system_to_entity(model: SystemModel) -> System:
    return System(
        id=model.id,
        equipment_id=model.equipment_id,
        name=model.name,
        status=model.status,
    )
