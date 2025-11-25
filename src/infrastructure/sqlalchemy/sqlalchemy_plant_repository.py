"""Implementación de `PlantRepository` usando SQLAlchemy y MySQL."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from src.entities.area import Area
from src.entities.equipment import Equipment
from src.entities.plant import Plant
from src.entities.system import System
from src.use_cases.ports.plant_repository import PlantRepository
from src.infrastructure.sqlalchemy.models import AreaModel, EquipmentModel, PlantModel, SystemModel


class SqlAlchemyPlantRepository(PlantRepository):
    """Repositorio concreto respaldado por MySQL."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    # Plant operations
    def list_plants(self) -> Sequence[Plant]:
        with self._session_factory() as session:
            rows = session.execute(select(PlantModel)).scalars().all()
            return [_to_plant(row) for row in rows]

    def get_plant(self, plant_id: int) -> Plant | None:
        with self._session_factory() as session:
            plant = session.get(PlantModel, plant_id)
            if plant is None:
                return None
            return _to_plant(plant)

    def create_plant(
        self,
        *,
        name: str,
        location: str | None = None,
        status: str | None = None,
    ) -> Plant:
        with self._session_factory() as session, session.begin():
            plant = PlantModel(name=name, location=location, status=status or "operativa")
            session.add(plant)
            session.flush()
            return _to_plant(plant)

    def update_plant(
        self,
        plant_id: int,
        *,
        name: str | None = None,
        location: str | None = None,
        status: str | None = None,
    ) -> Plant | None:
        with self._session_factory() as session, session.begin():
            plant = session.get(PlantModel, plant_id)
            if plant is None:
                return None

            if name is not None:
                plant.name = name
            if location is not None:
                plant.location = location
            if status is not None:
                plant.status = status

            session.flush()
            return _to_plant(plant)

    def delete_plant(self, plant_id: int) -> bool:
        with self._session_factory() as session, session.begin():
            plant = session.get(PlantModel, plant_id)
            if plant is None:
                return False

            session.delete(plant)
            return True

    # Area operations
    def list_areas(self, plant_id: int) -> Sequence[Area]:
        with self._session_factory() as session:
            rows = session.execute(
                select(AreaModel).where(AreaModel.plant_id == plant_id)
            ).scalars()
            return [_to_area(row) for row in rows]

    def get_area(self, area_id: int) -> Area | None:
        with self._session_factory() as session:
            area = session.get(AreaModel, area_id)
            if area is None:
                return None
            return _to_area(area)

    def create_area(
        self,
        plant_id: int,
        *,
        name: str,
        status: str | None = None,
    ) -> Area | None:
        with self._session_factory() as session, session.begin():
            plant = session.get(PlantModel, plant_id)
            if plant is None:
                return None

            area = AreaModel(plant_id=plant.id, name=name, status=status or "operativa")
            session.add(area)
            session.flush()
            return _to_area(area)

    def update_area(
        self,
        area_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> Area | None:
        with self._session_factory() as session, session.begin():
            area = session.get(AreaModel, area_id)
            if area is None:
                return None

            if name is not None:
                area.name = name
            if status is not None:
                area.status = status

            session.flush()
            return _to_area(area)

    def delete_area(self, area_id: int) -> bool:
        with self._session_factory() as session, session.begin():
            area = session.get(AreaModel, area_id)
            if area is None:
                return False

            session.delete(area)
            return True

    # Equipment operations
    def list_equipment(self, area_id: int) -> Sequence[Equipment]:
        with self._session_factory() as session:
            rows = session.execute(
                select(EquipmentModel).where(EquipmentModel.area_id == area_id)
            ).scalars()
            return [_to_equipment(row) for row in rows]

    def get_equipment(self, equipment_id: int) -> Equipment | None:
        with self._session_factory() as session:
            equipment = session.get(EquipmentModel, equipment_id)
            if equipment is None:
                return None
            return _to_equipment(equipment)

    def create_equipment(
        self,
        area_id: int,
        *,
        name: str,
        status: str | None = None,
    ) -> Equipment | None:
        with self._session_factory() as session, session.begin():
            area = session.get(AreaModel, area_id)
            if area is None:
                return None

            equipment = EquipmentModel(
                area_id=area.id, name=name, status=status or "operativo"
            )
            session.add(equipment)
            session.flush()
            return _to_equipment(equipment)

    def update_equipment(
        self,
        equipment_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> Equipment | None:
        with self._session_factory() as session, session.begin():
            equipment = session.get(EquipmentModel, equipment_id)
            if equipment is None:
                return None

            if name is not None:
                equipment.name = name
            if status is not None:
                equipment.status = status

            session.flush()
            return _to_equipment(equipment)

    def delete_equipment(self, equipment_id: int) -> bool:
        with self._session_factory() as session, session.begin():
            equipment = session.get(EquipmentModel, equipment_id)
            if equipment is None:
                return False

            session.delete(equipment)
            return True

    # System operations
    def list_systems(self, equipment_id: int) -> Sequence[System]:
        with self._session_factory() as session:
            rows = session.execute(
                select(SystemModel).where(SystemModel.equipment_id == equipment_id)
            ).scalars()
            return [_to_system(row) for row in rows]

    def get_system(self, system_id: int) -> System | None:
        with self._session_factory() as session:
            system = session.get(SystemModel, system_id)
            if system is None:
                return None
            return _to_system(system)

    def create_system(
        self,
        equipment_id: int,
        *,
        name: str,
        status: str | None = None,
    ) -> System | None:
        with self._session_factory() as session, session.begin():
            equipment = session.get(EquipmentModel, equipment_id)
            if equipment is None:
                return None

            system = SystemModel(
                equipment_id=equipment.id, name=name, status=status or "operativo"
            )
            session.add(system)
            session.flush()
            return _to_system(system)

    def update_system(
        self,
        system_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> System | None:
        with self._session_factory() as session, session.begin():
            system = session.get(SystemModel, system_id)
            if system is None:
                return None

            if name is not None:
                system.name = name
            if status is not None:
                system.status = status

            session.flush()
            return _to_system(system)

    def delete_system(self, system_id: int) -> bool:
        with self._session_factory() as session, session.begin():
            system = session.get(SystemModel, system_id)
            if system is None:
                return False

            session.delete(system)
            return True


def _to_plant(model: PlantModel) -> Plant:
    return Plant(
        id=model.id,
        name=model.name,
        location=model.location or "",
        status=model.status,
    )


def _to_area(model: AreaModel) -> Area:
    return Area(
        id=model.id,
        plant_id=model.plant_id,
        name=model.name,
        status=model.status,
    )


def _to_equipment(model: EquipmentModel) -> Equipment:
    return Equipment(
        id=model.id,
        area_id=model.area_id,
        name=model.name,
        status=model.status,
    )


def _to_system(model: SystemModel) -> System:
    return System(
        id=model.id,
        equipment_id=model.equipment_id,
        name=model.name,
        status=model.status,
    )
