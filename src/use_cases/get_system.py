"""Use case for retrieving a single system."""

from src.entities.system import System
from src.use_cases.ports.plant_repository import PlantRepository


class GetSystemUseCase:
    """Fetch a system by its identifier."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, system_id: int) -> System | None:
        return self._repository.get_system(system_id)
