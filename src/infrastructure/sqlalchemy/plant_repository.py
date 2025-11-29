"""Implementación de PlantRepository basada en SQLAlchemy."""

from __future__ import annotations

from collections.abc import Sequence
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.area import Area
from src.entities.equipment import Equipment
from src.entities.plant import Plant
from src.entities.system import System
from src.infrastructure.sqlalchemy import mappers
from src.infrastructure.sqlalchemy.session import SessionFactory
from src.infrastructure.sqlalchemy.models import (
    AreaModel,
    EquipmentModel,
    PlantModel,
    SystemModel,
)
from src.use_cases.ports.plant_repository import PlantDataRepository


class SqlAlchemyPlantRepository(PlantDataRepository):
    """Repositorio concreto respaldado por SQLAlchemy y MySQL."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @contextmanager
    def _session_scope(self, session: Session | None):
        if session is not None:
            yield session
        else:
            with self._session_factory() as new_session:
                yield new_session

    @contextmanager
    def _transactional_scope(self, session: Session | None):
        if session is not None:
            yield session
        else:
            with self._session_factory() as new_session, new_session.begin():
                yield new_session

    # Plant operations
    def list_plants(self, *, session: Session | None = None) -> Sequence[Plant]:
        with self._session_scope(session) as db:
            rows = db.execute(select(PlantModel)).scalars().all()
            return [mappers.plant_to_entity(row) for row in rows]

    def get_plant(
        self, plant_id: int, *, session: Session | None = None
    ) -> Plant | None:
        with self._session_scope(session) as db:
            plant = db.get(PlantModel, plant_id)
            if plant is None:
                return None
            return mappers.plant_to_entity(plant)

    def create_plant(
        self,
        *,
        name: str,
        location: str | None = None,
        status: str | None = None,
        session: Session | None = None,
    ) -> Plant:
        with self._transactional_scope(session) as db:
            plant = PlantModel(
                name=name, location=location, status=status or "operativa"
            )
            db.add(plant)
            db.flush()
            return mappers.plant_to_entity(plant)

    def update_plant(
        self,
        plant_id: int,
        *,
        name: str | None = None,
        location: str | None = None,
        status: str | None = None,
        session: Session | None = None,
    ) -> Plant | None:
        with self._transactional_scope(session) as db:
            plant = db.get(PlantModel, plant_id)
            if plant is None:
                return None

            if name is not None:
                plant.name = name
            if location is not None:
                plant.location = location
            if status is not None:
                plant.status = status

            db.flush()
            return mappers.plant_to_entity(plant)

    def delete_plant(self, plant_id: int, *, session: Session | None = None) -> bool:
        with self._transactional_scope(session) as db:
            plant = db.get(PlantModel, plant_id)
            if plant is None:
                return False

            db.delete(plant)
            return True

    # Area operations
    def list_areas(
        self, plant_id: int, *, session: Session | None = None
    ) -> Sequence[Area]:
        with self._session_scope(session) as db:
            rows = db.execute(
                select(AreaModel).where(AreaModel.plant_id == plant_id)
            ).scalars()
            return [mappers.area_to_entity(row) for row in rows]

    def get_area(self, area_id: int, *, session: Session | None = None) -> Area | None:
        with self._session_scope(session) as db:
            area = db.get(AreaModel, area_id)
            if area is None:
                return None
            return mappers.area_to_entity(area)

    def create_area(
        self,
        plant_id: int,
        *,
        name: str,
        status: str | None = None,
        session: Session | None = None,
    ) -> Area | None:
        with self._transactional_scope(session) as db:
            plant = db.get(PlantModel, plant_id)
            if plant is None:
                return None

            area = AreaModel(plant_id=plant.id, name=name, status=status or "operativa")
            db.add(area)
            db.flush()
            return mappers.area_to_entity(area)

    def update_area(
        self,
        area_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
        session: Session | None = None,
    ) -> Area | None:
        with self._transactional_scope(session) as db:
            area = db.get(AreaModel, area_id)
            if area is None:
                return None

            if name is not None:
                area.name = name
            if status is not None:
                area.status = status

            db.flush()
            return mappers.area_to_entity(area)

    def delete_area(self, area_id: int, *, session: Session | None = None) -> bool:
        with self._transactional_scope(session) as db:
            area = db.get(AreaModel, area_id)
            if area is None:
                return False

            db.delete(area)
            return True

    # Equipment operations
    def list_equipment(
        self, area_id: int, *, session: Session | None = None
    ) -> Sequence[Equipment]:
        with self._session_scope(session) as db:
            rows = db.execute(
                select(EquipmentModel).where(EquipmentModel.area_id == area_id)
            ).scalars()
            return [mappers.equipment_to_entity(row) for row in rows]

    def get_equipment(
        self, equipment_id: int, *, session: Session | None = None
    ) -> Equipment | None:
        with self._session_scope(session) as db:
            equipment = db.get(EquipmentModel, equipment_id)
            if equipment is None:
                return None
            return mappers.equipment_to_entity(equipment)

    def create_equipment(
        self,
        area_id: int,
        *,
        name: str,
        status: str | None = None,
        session: Session | None = None,
    ) -> Equipment | None:
        with self._transactional_scope(session) as db:
            area = db.get(AreaModel, area_id)
            if area is None:
                return None

            equipment = EquipmentModel(
                area_id=area.id, name=name, status=status or "operativo"
            )
            db.add(equipment)
            db.flush()
            return mappers.equipment_to_entity(equipment)

    def update_equipment(
        self,
        equipment_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
        session: Session | None = None,
    ) -> Equipment | None:
        with self._transactional_scope(session) as db:
            equipment = db.get(EquipmentModel, equipment_id)
            if equipment is None:
                return None

            if name is not None:
                equipment.name = name
            if status is not None:
                equipment.status = status

            db.flush()
            return mappers.equipment_to_entity(equipment)

    def delete_equipment(
        self, equipment_id: int, *, session: Session | None = None
    ) -> bool:
        with self._transactional_scope(session) as db:
            equipment = db.get(EquipmentModel, equipment_id)
            if equipment is None:
                return False

            db.delete(equipment)
            return True

    # System operations
    def list_systems(
        self, equipment_id: int, *, session: Session | None = None
    ) -> Sequence[System]:
        with self._session_scope(session) as db:
            rows = db.execute(
                select(SystemModel).where(SystemModel.equipment_id == equipment_id)
            ).scalars()
            return [mappers.system_to_entity(row) for row in rows]

    def get_system(
        self, system_id: int, *, session: Session | None = None
    ) -> System | None:
        with self._session_scope(session) as db:
            system = db.get(SystemModel, system_id)
            if system is None:
                return None
            return mappers.system_to_entity(system)

    def create_system(
        self,
        equipment_id: int,
        *,
        name: str,
        status: str | None = None,
        session: Session | None = None,
    ) -> System | None:
        with self._transactional_scope(session) as db:
            equipment = db.get(EquipmentModel, equipment_id)
            if equipment is None:
                return None

            system = SystemModel(
                equipment_id=equipment.id, name=name, status=status or "operativo"
            )
            db.add(system)
            db.flush()
            return mappers.system_to_entity(system)

    def update_system(
        self,
        system_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
        session: Session | None = None,
    ) -> System | None:
        with self._transactional_scope(session) as db:
            system = db.get(SystemModel, system_id)
            if system is None:
                return None

            if name is not None:
                system.name = name
            if status is not None:
                system.status = status

            db.flush()
            return mappers.system_to_entity(system)

    def delete_system(self, system_id: int, *, session: Session | None = None) -> bool:
        with self._transactional_scope(session) as db:
            system = db.get(SystemModel, system_id)
            if system is None:
                return False

            db.delete(system)
            return True
