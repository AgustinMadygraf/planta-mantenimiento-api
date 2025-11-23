"""Use case for updating system information."""

from src.entities.system import System
from src.use_cases.ports.plant_repository import PlantRepository


class UpdateSystemUseCase:
    """Apply updates to a system record."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, system_id: int, *, name: str | None = None, status: str | None = None) -> System | None:
        return self._repository.update_system(system_id, name=name, status=status)
