"""Simple in-memory repository for development and testing."""

from typing import Sequence

from src.entities.plant import Plant
from src.use_cases.list_plants import PlantRepository


class InMemoryPlantRepository(PlantRepository):
    """Provide a predictable data set without hitting a real database."""

    _PLANTS: tuple[Plant, ...] = (
        Plant(id=1, name="Planta Norte", location="Zona Industrial A", status="operativa"),
        Plant(id=2, name="Planta Sur", location="Zona Industrial B", status="mantenimiento"),
        Plant(id=3, name="Planta Este", location="Zona Industrial C", status="operativa"),
    )

    def list_plants(self) -> Sequence[Plant]:
        return list(self._PLANTS)
