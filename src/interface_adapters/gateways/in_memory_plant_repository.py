"""Simple in-memory repository for development and testing."""

from __future__ import annotations

from typing import Sequence

from src.entities.area import Area
from src.entities.plant import Plant
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

    def list_plants(self) -> Sequence[Plant]:
        return list(self._plants.values())

    def get_plant(self, plant_id: int) -> Plant | None:
        return self._plants.get(plant_id)

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

    def list_areas(self, plant_id: int) -> Sequence[Area]:
        return list(self._areas.get(plant_id, ()))
