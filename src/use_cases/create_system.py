"""Use case for creating new systems."""

from src.entities.system import System
from src.use_cases.ports.plant_repository import PlantRepository


class CreateSystemUseCase:
    """Create a system associated with equipment."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, equipment_id: int, *, name: str, status: str | None = None) -> System | None:
        return self._repository.create_system(equipment_id, name=name, status=status)
