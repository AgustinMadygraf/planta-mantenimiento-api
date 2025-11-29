"""Repository contracts segmented by aggregate root.

Separar las operaciones por agregado reduce el acoplamiento entre casos de uso
y la infraestructura de persistencia, permitiendo que cada caso de uso dependa
solo de los métodos que necesita.
"""

from typing import Protocol, Sequence

from src.entities.area import Area
from src.entities.equipment import Equipment
from src.entities.plant import Plant
from src.entities.system import System


class PlantRepository(Protocol):
    """Expose only plant operations needed by the use cases."""

    def list_plants(self) -> Sequence[Plant]:
        ...

    def get_plant(self, plant_id: int) -> Plant | None:
        ...

    def create_plant(
        self,
        *,
        name: str,
        location: str | None = None,
        status: str | None = None,
    ) -> Plant:
        ...

    def update_plant(
        self,
        plant_id: int,
        *,
        name: str | None = None,
        location: str | None = None,
        status: str | None = None,
    ) -> Plant | None:
        ...

    def delete_plant(self, plant_id: int) -> bool:
        ...


class AreaRepository(Protocol):
    """Contract for manipulating areas within a plant."""

    def list_areas(self, plant_id: int) -> Sequence[Area]:
        ...

    def get_area(self, area_id: int) -> Area | None:
        ...

    def create_area(
        self,
        plant_id: int,
        *,
        name: str,
        status: str | None = None,
    ) -> Area | None:
        ...

    def update_area(
        self,
        area_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> Area | None:
        ...

    def delete_area(self, area_id: int) -> bool:
        ...


class EquipmentRepository(Protocol):
    """Contract for working with equipment of an area."""

    def list_equipment(self, area_id: int) -> Sequence[Equipment]:
        ...

    def get_equipment(self, equipment_id: int) -> Equipment | None:
        ...

    def create_equipment(
        self,
        area_id: int,
        *,
        name: str,
        status: str | None = None,
    ) -> Equipment | None:
        ...

    def update_equipment(
        self,
        equipment_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> Equipment | None:
        ...

    def delete_equipment(self, equipment_id: int) -> bool:
        ...


class SystemRepository(Protocol):
    """Contract for managing systems linked to equipment."""

    def list_systems(self, equipment_id: int) -> Sequence[System]:
        ...

    def get_system(self, system_id: int) -> System | None:
        ...

    def create_system(
        self,
        equipment_id: int,
        *,
        name: str,
        status: str | None = None,
    ) -> System | None:
        ...

    def update_system(
        self,
        system_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> System | None:
        ...

    def delete_system(self, system_id: int) -> bool:
        ...


class PlantDataRepository(
    PlantRepository, AreaRepository, EquipmentRepository, SystemRepository, Protocol
):
    """Composite protocol used by controllers that need all aggregates."""

    pass


__all__ = [
    "PlantRepository",
    "AreaRepository",
    "EquipmentRepository",
    "SystemRepository",
    "PlantDataRepository",
]
