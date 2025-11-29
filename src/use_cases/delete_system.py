"""Use case for deleting a system."""

from src.use_cases.ports.plant_repository import SystemRepository


class DeleteSystemUseCase:
    """Remove a system from its equipment."""

    def __init__(self, repository: SystemRepository) -> None:
        self._repository = repository

    def execute(self, system_id: int) -> bool:
        return self._repository.delete_system(system_id)
