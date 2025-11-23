"""Use case for listing the areas of a plant."""

from typing import Sequence

from src.entities.area import Area
from src.use_cases.ports.plant_repository import PlantRepository


class ListPlantAreasUseCase:
    """Retrieve the areas belonging to a plant."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, plant_id: int) -> Sequence[Area]:
        return self._repository.list_areas(plant_id)
