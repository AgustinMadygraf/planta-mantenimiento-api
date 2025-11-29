"""Use case for deleting an area."""

from src.use_cases.ports.plant_repository import AreaRepository


class DeleteAreaUseCase:
    """Remove an area and its dependencies."""

    def __init__(self, repository: AreaRepository) -> None:
        self._repository = repository

    def execute(self, area_id: int) -> bool:
        return self._repository.delete_area(area_id)
