"""Repository contract for plant-related operations."""

from typing import Protocol, Sequence

from src.entities.area import Area
from src.entities.plant import Plant


class PlantRepository(Protocol):
    """Expose plant data operations needed by the use cases."""

    def list_plants(self) -> Sequence[Plant]:
        ...

    def get_plant(self, plant_id: int) -> Plant | None:
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

    def list_areas(self, plant_id: int) -> Sequence[Area]:
        ...
