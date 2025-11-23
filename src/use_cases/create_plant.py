"""Use case for registering a new plant."""

from src.entities.plant import Plant
from src.use_cases.ports.plant_repository import PlantRepository


class CreatePlantUseCase:
    """Create a plant using the repository contract."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, *, name: str, location: str | None = None, status: str | None = None) -> Plant:
        return self._repository.create_plant(name=name, location=location, status=status)
