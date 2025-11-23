"""Use case for creating a new area within a plant."""

from src.entities.area import Area
from src.use_cases.ports.plant_repository import PlantRepository


class CreateAreaUseCase:
    """Create an area associated with a plant."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, plant_id: int, *, name: str, status: str | None = None) -> Area | None:
        return self._repository.create_area(plant_id, name=name, status=status)
