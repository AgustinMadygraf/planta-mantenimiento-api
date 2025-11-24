"""Simple in-memory repository for development and testing."""

from __future__ import annotations

from typing import Sequence

from src.entities.area import Area
from src.entities.equipment import Equipment
from src.entities.plant import Plant
from src.entities.system import System
from src.use_cases.ports.plant_repository import PlantRepository


class InMemoryPlantRepository(PlantRepository):
    """Provide a predictable data set without hitting a real database."""

    def __init__(self) -> None:
        self._plants: dict[int, Plant] = {
            1: Plant(id=1, name="Planta Norte", location="Zona Industrial A", status="operativa"),
            2: Plant(id=2, name="Planta Sur", location="Zona Industrial B", status="mantenimiento"),
            3: Plant(id=3, name="Planta Este", location="Zona Industrial C", status="operativa"),
        }
        self._areas: dict[int, tuple[Area, ...]] = {
            1: (
                Area(id=101, plant_id=1, name="Área de Producción", status="operativa"),
                Area(id=102, plant_id=1, name="Área de Almacenamiento", status="mantenimiento"),
            ),
            2: (
                Area(id=201, plant_id=2, name="Área de Seguridad", status="operativa"),
            ),
            3: (
                Area(id=301, plant_id=3, name="Área de Laboratorio", status="operativa"),
                Area(id=302, plant_id=3, name="Área de Logística", status="operativa"),
            ),
        }
        self._equipment: dict[int, tuple[Equipment, ...]] = {
            101: (
                Equipment(id=1001, area_id=101, name="Compresor A", status="operativo"),
                Equipment(id=1002, area_id=101, name="Banda Transportadora", status="mantenimiento"),
            ),
            201: (
                Equipment(id=2001, area_id=201, name="Tablero de Control", status="operativo"),
            ),
        }
        self._systems: dict[int, tuple[System, ...]] = {
            1001: (
                System(id=5001, equipment_id=1001, name="Sistema de Enfriamiento", status="operativo"),
            ),
        }

    # Plant operations
    def list_plants(self) -> Sequence[Plant]:
        return list(self._plants.values())

    def get_plant(self, plant_id: int) -> Plant | None:
        return self._plants.get(plant_id)

    def create_plant(
        self,
        *,
        name: str,
        location: str | None = None,
        status: str | None = None,
    ) -> Plant:
        new_id = max(self._plants.keys(), default=0) + 1
        plant = Plant(
            id=new_id,
            name=name,
            location=location or "",
            status=status or "operativa",
        )
        self._plants[new_id] = plant
        return plant

    def update_plant(
        self,
        plant_id: int,
        *,
        name: str | None = None,
        location: str | None = None,
        status: str | None = None,
    ) -> Plant | None:
        current = self._plants.get(plant_id)
        if current is None:
            return None

        updated = Plant(
            id=current.id,
            name=name if name is not None else current.name,
            location=location if location is not None else current.location,
            status=status if status is not None else current.status,
        )

        self._plants[plant_id] = updated
        return updated

    def delete_plant(self, plant_id: int) -> bool:
        if plant_id not in self._plants:
            return False

        # Cascade delete for areas, equipment and systems
        for area in self._areas.pop(plant_id, ()):  # remove areas for plant
            self._cascade_delete_area(area.id)

        del self._plants[plant_id]
        return True

    # Area operations
    def list_areas(self, plant_id: int) -> Sequence[Area]:
        return list(self._areas.get(plant_id, ()))

    def get_area(self, area_id: int) -> Area | None:
        for areas in self._areas.values():
            for area in areas:
                if area.id == area_id:
                    return area
        return None

    def create_area(
        self,
        plant_id: int,
        *,
        name: str,
        status: str | None = None,
    ) -> Area | None:
        plant = self._plants.get(plant_id)
        if plant is None:
            return None

        new_id = max((area.id for areas in self._areas.values() for area in areas), default=0) + 1
        area = Area(
            id=new_id,
            plant_id=plant.id,
            name=name,
            status=status or "operativa",
        )
        current = list(self._areas.get(plant_id, ()))
        current.append(area)
        self._areas[plant_id] = tuple(current)
        return area

    def update_area(
        self,
        area_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> Area | None:
        for plant_id, areas in self._areas.items():
            updated: list[Area] = []
            found = None
            for area in areas:
                if area.id == area_id:
                    found = Area(
                        id=area.id,
                        plant_id=area.plant_id,
                        name=name if name is not None else area.name,
                        status=status if status is not None else area.status,
                    )
                    updated.append(found)
                else:
                    updated.append(area)
            if found:
                self._areas[plant_id] = tuple(updated)
                return found
        return None

    def delete_area(self, area_id: int) -> bool:
        for plant_id, areas in list(self._areas.items()):
            filtered = [area for area in areas if area.id != area_id]
            if len(filtered) != len(areas):
                self._areas[plant_id] = tuple(filtered)
                self._cascade_delete_area(area_id)
                return True
        return False

    # Equipment operations
    def list_equipment(self, area_id: int) -> Sequence[Equipment]:
        return list(self._equipment.get(area_id, ()))

    def get_equipment(self, equipment_id: int) -> Equipment | None:
        for equipment_list in self._equipment.values():
            for equipment in equipment_list:
                if equipment.id == equipment_id:
                    return equipment
        return None

    def create_equipment(
        self,
        area_id: int,
        *,
        name: str,
        status: str | None = None,
    ) -> Equipment | None:
        area = self.get_area(area_id)
        if area is None:
            return None

        new_id = max((eq.id for items in self._equipment.values() for eq in items), default=0) + 1
        equipment = Equipment(
            id=new_id,
            area_id=area.id,
            name=name,
            status=status or "operativo",
        )
        current = list(self._equipment.get(area_id, ()))
        current.append(equipment)
        self._equipment[area_id] = tuple(current)
        return equipment

    def update_equipment(
        self,
        equipment_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> Equipment | None:
        for area_id, equipments in self._equipment.items():
            updated: list[Equipment] = []
            found = None
            for equipment in equipments:
                if equipment.id == equipment_id:
                    found = Equipment(
                        id=equipment.id,
                        area_id=equipment.area_id,
                        name=name if name is not None else equipment.name,
                        status=status if status is not None else equipment.status,
                    )
                    updated.append(found)
                else:
                    updated.append(equipment)
            if found:
                self._equipment[area_id] = tuple(updated)
                return found
        return None

    def delete_equipment(self, equipment_id: int) -> bool:
        for area_id, equipments in list(self._equipment.items()):
            filtered = [eq for eq in equipments if eq.id != equipment_id]
            if len(filtered) != len(equipments):
                self._equipment[area_id] = tuple(filtered)
                self._systems.pop(equipment_id, None)
                return True
        return False

    # System operations
    def list_systems(self, equipment_id: int) -> Sequence[System]:
        return list(self._systems.get(equipment_id, ()))

    def get_system(self, system_id: int) -> System | None:
        for systems in self._systems.values():
            for system in systems:
                if system.id == system_id:
                    return system
        return None

    def create_system(
        self,
        equipment_id: int,
        *,
        name: str,
        status: str | None = None,
    ) -> System | None:
        equipment = self.get_equipment(equipment_id)
        if equipment is None:
            return None

        new_id = max((sys.id for systems in self._systems.values() for sys in systems), default=0) + 1
        system = System(
            id=new_id,
            equipment_id=equipment.id,
            name=name,
            status=status or "operativo",
        )
        current = list(self._systems.get(equipment_id, ()))
        current.append(system)
        self._systems[equipment_id] = tuple(current)
        return system

    def update_system(
        self,
        system_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> System | None:
        for equipment_id, systems in self._systems.items():
            updated: list[System] = []
            found = None
            for system in systems:
                if system.id == system_id:
                    found = System(
                        id=system.id,
                        equipment_id=system.equipment_id,
                        name=name if name is not None else system.name,
                        status=status if status is not None else system.status,
                    )
                    updated.append(found)
                else:
                    updated.append(system)
            if found:
                self._systems[equipment_id] = tuple(updated)
                return found
        return None

    def delete_system(self, system_id: int) -> bool:
        for equipment_id, systems in list(self._systems.items()):
            filtered = [sys for sys in systems if sys.id != system_id]
            if len(filtered) != len(systems):
                self._systems[equipment_id] = tuple(filtered)
                return True
        return False

    # Helpers
    def _cascade_delete_area(self, area_id: int) -> None:
        equipment_in_area = self._equipment.pop(area_id, ())
        for equipment in equipment_in_area:
            self._systems.pop(equipment.id, None)
