"""Use case for retrieving a single plant."""

from src.entities.plant import Plant
from src.use_cases.ports.plant_repository import PlantRepository


class GetPlantUseCase:
    """Fetch a plant by its identifier."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, plant_id: int) -> Plant | None:
        return self._repository.get_plant(plant_id)
